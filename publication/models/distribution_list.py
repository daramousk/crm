# -*- coding: utf-8 -*-
# Copyright 2014-2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


SQL_CONTRACT_COUNT = """
SELECT COALESCE(SUM(ROUND(l.quantity)::integer), 0) as quantity
 FROM account_analytic_invoice_line l
 JOIN account_analytic_account c
 ON l.contract_id = c.id
 WHERE l.product_id = %s
 AND c.partner_id = %s"""

SQL_ASSIGNED_COUNT = """
SELECT COALESCE(SUM(copies), 0) as copies
 FROM distribution_list
 WHERE product_id = %s
 AND contract_partner_id = %s"""


class DistributionList(models.Model):
    _name = 'distribution.list'
    _inherit = ['active.date']
    _order = 'name'

    @api.depends('product_id', 'partner_id')
    def _compute_name_address(self):
        """Create subscription name from publication and partner."""
        for this in self:
            if not this.product_id or not this.partner_id:
                this.name = False
                this.display_address = False
                continue
            this.name = ' - '.join(
                [this.product_id.name, this.partner_id.name])
            if this.product_id.distribution_type == 'email':
                this.display_address = this.partner_id.email
            else:
                this.display_address = this.partner_id.contact_address

    @api.multi
    @api.depends('product_id', 'contract_partner_id', 'copies')
    def _compute_counts(self):
        """Used to check how many addresses can still be added."""
        cr = self.env.cr
        for this in self:
            if not self.product_id or not self.contract_partner_id:
                continue
            cr.execute(
                SQL_CONTRACT_COUNT,
                (this.product_id.id, this.contract_partner_id.id))
            contract_count = cr.fetchone()[0]
            cr.execute(
                SQL_ASSIGNED_COUNT,
                (this.product_id.id, this.contract_partner_id.id))
            assigned_count = cr.fetchone()[0]
            available_count = contract_count - assigned_count
            this.contract_count = contract_count
            this.assigned_count = assigned_count
            this.available_count = available_count

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Publication',
        domain=[('publication', '=', True)],
        required=True)
    distribution_type = fields.Selection(
        string='Type of publication',
        related='product_id.distribution_type',
        store=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Receiving Partner',
        required=True)
    contract_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contract Partner',
        required=True)
    # override active_date_start with extra atributed
    active_date_start = fields.Date(
        string='Date start',
        default=fields.Date.today(),
        required=True)
    copies = fields.Integer(string='Number of copies', default=1)
    name = fields.Char(
        compute='_compute_name_address',
        string='Name')
    display_address = fields.Char(
        compute='_compute_name_address',
        string='Receiving address')
    contract_count = fields.Integer(
        string="Number to distribute",
        compute='_compute_counts')
    assigned_count = fields.Integer(
        string="Number already assigned",
        compute='_compute_counts')
    available_count = fields.Integer(
        string="Number still available",
        compute='_compute_counts')

    @api.onchange('product_id', 'contract_partner_id')
    def _onchange_keyfields(self):
        """Sets the proper domain for contract_partner.

        Also enforces first selecting the publication.
        """
        self.ensure_one()
        if self.contract_partner_id and not self.partner_id:
            self.partner_id = self.contract_partner_id
        if self.contract_partner_id and not self.product_id:
            raise ValidationError(_(
                "You must select a publication, before selecting"
                " the contract partner."))
        if not self.product_id:
            return
        valid_partners = []
        line_model = self.env['account.analytic.invoice.line']
        lines = line_model.search([('product_id', '=', self.product_id.id)])
        for line in lines:
            if line.contract_id.partner_id.id not in valid_partners:
                valid_partners.append(line.contract_id.partner_id.id)
        if not valid_partners:
            raise ValidationError(_(
                "There are no active subscriptions for this publication."))
        partner_domain = [('id', 'in', valid_partners)]
        return {'domain': {'contract_partner_id': partner_domain}}

    @api.constrains('product_id', 'contract_partner_id', 'copies')
    @api.multi
    def _limit_count(self):
        """Limit number of copies send to amount set in contract lines."""
        for this in self:
            if self.available_count < 0:
                raise ValidationError(_(
                    "Number of copies sent %d can not exceed contracted"
                    " number %d for partner %s and product %s" % (
                        self.assigned_count,
                        self.contract_count,
                        self.contract_partner_id.display_name,
                        self.product_id.display_name)))
