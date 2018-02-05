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
    def active_change_trigger(self):
        """Postprocess records immediately after changing active field.

        Make sure membership recomputed for affected partners.
        This method will also always be called on create.
        """
        super(AccountAnalyticInvoiceLine, self).active_change_trigger()
        for this in self:
            if this.membership:
                this.partner_id._compute_membership()

    @api.multi
    def membership_change_trigger(self, create=False):
        """Postprocess records immediately after changing membership field.

        Make sure membership correctly set on partner.
        """
        for this in self:
            this.partner_id._compute_membership(create=create)

    @api.multi
    def write(self, vals):
        if 'membership' not in vals:
            return super(AccountAnalyticInvoiceLine, self).write(vals)
        for this in self:
            save_membership = this.membership
            super(AccountAnalyticInvoiceLine, this).write(vals)
            if this.membership != save_membership:
                this.membership_change_trigger()
        return True

    @api.multi
    def unlink(self):
        """Unlinking might effect membership."""
        for this in self:
            if this.membership:
                partner = this.partner_id
                super(AccountAnalyticInvoiceLine, this).unlink()
                partner._compute_membership()
            else:
                super(AccountAnalyticInvoiceLine, this).unlink()
