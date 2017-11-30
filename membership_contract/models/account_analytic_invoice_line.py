# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = 'account.analytic.invoice.line'

    membership = fields.Boolean(
        string='Membership product line',
        related='product_id.membership',
        store=True)
