# -*- coding: utf-8 -*-
# Copyright 2014-2019 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# pylint: disable=no-member
from odoo import api, fields, models


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = 'account.analytic.invoice.line'

    publication = fields.Boolean(
        string='Subscription product line',
        related='product_id.publication',
        store=True)

    @api.multi
    def action_distribution_list(self):
        self.ensure_one()
        action = self.env.ref(
            'publication.action_distribution_list').read()[0]
        partner = self.analytic_account_id.partner_id
        action['context'] = {
            'default_product_id': self.product_id.id,
            'default_contract_partner_id': partner.id}
        action['domain'] = [
            ('contract_partner_id', '=', partner.id),
            ('product_id', '=', self.product_id.id)]
        action['view_mode'] = 'form'
        action['target'] = 'current'
        return action

    @api.model
    def create(self, vals):
        result = super(AccountAnalyticInvoiceLine, self).create(vals)
        if result.publication:
            self._update_publication_list()
        return result

    @api.multi
    def write(self, vals):
        p_product = self.env['product.product']
        d_list = self.env['distribution.list']
        product_id = vals.get('product_id')
        # if the user set changed the product to a non publication product
        # we need to find and delete the corresponding publication list
        if product_id and not p_product.browse(
                product_id).publication:
            contract_partner_ids = self.mapped(
                'analytic_account_id').mapped('partner_id').ids
            line_partner_ids = self.mapped('partner_id').ids
            product_ids = self.mapped('product_id').ids
            d_list.search([
                ('contract_partner_id', 'in', contract_partner_ids),
                ('partner_id', 'in', line_partner_ids),
                ('product_id', 'in', product_ids),
            ]).unlink()
        else:
            self._update_publication_list(vals)
        return super(AccountAnalyticInvoiceLine, self).write(vals)

    @api.multi
    def _update_publication_list(self, vals=None):
        """ Conditionally creates a publication list:
        If a list with the same contract_partner_id, product_id and
        partner_id exists go write on that, else create a new one.
        """
        d_list = self.env['distribution.list']
        acc_analytic = self.env['account.analytic.account']
        for rec in self:
            account_id = vals.get('analytic_account_id') \
                or rec.analytic_account_id.id
            contract_partner_id = acc_analytic.browse(account_id).partner_id.id
            product_id = vals.get('product_id') or rec.product_id.id
            partner_id = vals.get('partner_id') or rec.partner_id.id
            # see if there already exists a publication list
            pub_list = d_list.search([
                ('contract_partner_id', '=', contract_partner_id),
                ('product_id', '=', product_id),
                ('partner_id', '=', partner_id),
            ], limit=1)
            # if it does, just update it's quantity, else create it
            if pub_list:
                pub_list.write({'copies': pub_list.copies + rec.quantity})
            else:
                d_list.create({
                    'contract_partner_id': contract_partner_id,
                    'product_id': product_id,
                    'partner_id': partner_id,
                    'copies': rec.quantity,
                })

    @api.multi
    def unlink(self):
        records = self.filtered(lambda x: x.publication is True)
        for rec in records:
            # since there is no one2one relationship between the
            # publication lists and the account lines, we need
            # to reduce the copies of each distribution list by
            # the quantity on the deleted account line.
            _qty_to_remove = rec.quantity
            for d_list in self.env['distribution.list'].search([
                    ('contract_partner_id',
                        '=',
                        rec.analytic_account_id.partner_id.id),
                    ('product_id', '=', rec.product_id.id),
                    ('partner_id', '=', rec.partner_id.id)],
                    order='copies DESC'):
                if _qty_to_remove > d_list.copies:
                    _qty_to_remove -= d_list.copies
                    d_list.unlink()
                else:
                    d_list.copies -= _qty_to_remove
                    break
        return super(AccountAnalyticInvoiceLine, self).unlink()
