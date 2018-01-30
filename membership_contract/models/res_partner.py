# -*- coding: utf-8 -*-
# Copyright 2017-2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    membership = fields.Boolean(
        string='Is member?',
        readonly=True)
    associate_member = fields.Many2one(
        comodel_name='res.partner',
        string='Member via partner',
        readonly=True,
        index=True)
    membership_line_ids = fields.One2many(
        comodel_name='account.analytic.invoice.line',
        inverse_name='partner_id',
        domain=[('membership', '=', True)],
        string='Membership contract lines')

    @api.multi
    def membership_change_trigger(self, create=False):
        """Allows other models to react on change in membership state.

        This method is meant to be overridden in other modules.
        """
        pass

    @api.multi
    def _compute_membership(self, create=False):
        # Prevent recursion due to repeated writes
        guarded_self = self
        guard_dict = self.env.context.get('guard_dict', None)
        if guard_dict is None:
            guard_dict = {}
            guarded_self = self.with_context(guard_dict=guard_dict)
        inner_guard_dict = guard_dict.get('_compute_membership', None)
        if inner_guard_dict is None:
            inner_guard_dict = {}
            guard_dict['_compute_membership'] = inner_guard_dict
        for this in guarded_self:
            if this.id in inner_guard_dict:
                continue
            inner_guard_dict[this.id] = True
            save_membership = this.membership
            membership = False
            for line in this.membership_line_ids:
                if line.active:  # Not dependend on active flag in context
                    membership = True
                    break
            if membership != save_membership or create:
                super(ResPartner, this).write({'membership': membership})
                this.membership_change_trigger(create=create)

    @api.model
    def create(self, vals):
        new_rec = super(ResPartner, self).create(vals)
        new_rec._compute_membership(create=True)
        return new_rec

    @api.multi
    def write(self, vals):
        result = super(ResPartner, self).write(vals)
        self._compute_membership()
        return result

    @api.multi
    def _compute_membership_price(
            self, company_id, product, quantity, price_unit, tax_id, date):
        """Recompute price taking membership prices into account.

        We will reuse the code Odoo has for computing the price unit per
        unit for a sale order line, by creating an in memory sale order.
        For each applicable membership pricelist, we will set this pricelist
        to the in memory sale order, and see which price results. The lowest
        price 'wins' and will be applied.
        """
        self.ensure_one()
        if not self.membership:
            return price_unit
        # Find applicable membership prices, if any
        membership_pricelists = []
        for line in self.membership_line_ids:
            if line.product_id.membership_pricelist_id and \
                    line.contract_id.company_id == company_id and \
                    line.contract_id.start_date <= date and \
                    (not line.contract_id.end_date or
                     line.contract_id.end_date > date) and \
                    line.product_id.membership_pricelist_id not in \
                    membership_pricelists:
                membership_pricelists.append(
                    line.product_id.membership_pricelist_id)
        if not membership_pricelists:
            return price_unit
        result_price_unit = price_unit
        for pricelist in membership_pricelists:
            virtual_order = self.env['sale.order'].new({
                'company_id': company_id,
                'partner_id': self.id,
                'date_order': date,
                'pricelist_id': pricelist.id})
            virtual_line = self.env['sale.order.line'].new({
                'order_id': virtual_order.id,
                'product_id': product.id,
                'product_uom_qty': quantity,
                'pricelist_id': pricelist.id})
