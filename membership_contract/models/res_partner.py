# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('membership_line_ids')
    def _compute_membership(self):
        for this in self:
            this.membership = bool(this.membership_line_ids)

    membership = fields.Boolean(
        string='Is member?',
        compute='_compute_membership')
    membership_line_ids = fields.One2many(
        comodel_name='account.analytic.invoice.line',
        inverse_name='partner_id',
        domain=[('membership', '=', True)],
        string='Membership contract lines')
