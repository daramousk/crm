# -*- coding: utf-8 -*-
# Copyright 2014-2017 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = 'account.analytic.invoice.line'

    @api.depends('product_id')
    def _compute_subscription_product_line(self):
        """Check wether contract line is for a publication."""
        publication_model = self.env['publication.publication']
        for this in self:
            publication = publication_model.search(
                [('product_id', '=', this.id)], limit=1)
            this.subscription_product_line = bool(publication)

    @api.multi
    def _compute_partner_id(self):
        """We need this, because reference to contract is broken."""
        partner_model = self.env['res.partner']
        for this in self:
            # Hack based on fact that database field not corrupted:
            partner_id = self.env.cr.execute(
                "SELECT aaa.partner_id"
                " FROM account_analytic_invoice_line aail"
                " JOIN account_analytic_account aaa"
                "     ON aail.analytic_account_id = aaa.id"
                " WHERE aail.id = %s",
                this.id)
            partner = partner_model.browse([partner_id[0]])
            this.partner_id = partner

    subscription_product_line = fields.Boolean(
        string='Subscription product line',
        compute='_compute_subscription_product_line',
        store=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        compute='_compute_partner_id',
        string='Partner')