# -*- coding: utf-8 -*-
# Copyright 2017-2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('membership_line_ids')
    def _compute_membership(self):
        for this in self:
            this.hierarchy_membership = False
            save_membership = this.membership
            super(ResPartner, this)._compute_membership()
            if not this.membership:
                # Might still be member through partner above
                for partner_above in this.partner_above_ids:
                    if partner_above.partner_above_id.membership:
                        this.membership = True
                        this.hierarchy_membership = True
                        this.associate_member = partner_above.partner_above_id
                        break
            if this.membership != save_membership:
                # We might need to change membership of associates
                linked_members = self.search([
                    ('associate_member', '=', this.id),
                    ('hierarchy_membership', '=', True)])
                for member in linked_members:
                    super(ResPartner, member)._compute_membership()

    hierarchy_membership = fields.Boolean(
        string='Membership through hierarchy',
        compute='_compute_membership',
        store=True)
