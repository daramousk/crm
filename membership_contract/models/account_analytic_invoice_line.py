# -*- coding: utf-8 -*-
# Copyright 2017-2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = 'account.analytic.invoice.line'

    membership = fields.Boolean(
        string='Membership product line',
        related='product_id.membership',
        store=True)

    @api.model
    def active_refresh_post_process(self, active_change_datetime):
        """Postprocess records immediately after changing active field.

        Make sure membership recomputed for affected partners.
        """
        super(AccountAnalyticInvoiceLine, self).active_refresh_post_process(
            active_change_datetime)
        lines = self.search([
            ('active_change_datetime', '=', active_change_datetime)])
        for line in lines:
            if line.membership:
                line.partner_id._compute_membership()
