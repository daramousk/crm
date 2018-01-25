# -*- coding: utf-8 -*-
# Copyright 2017-2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def membership_change_trigger(self):
        """Compute membership for members immediately below this one."""
        hierarchy_model = self.env['res.partner.relation.hierarchy']
        for this in self:
            partners_below = hierarchy_model.search([
                ('partner_above_id', '=', this.id),
                ('level', '=', 1)])
            for partner_below in partners_below:
                partner_below.partner_below_id._compute_membership()

    @api.multi
    def _compute_membership(self):
        for this in self:
            super(ResPartner, this)._compute_membership()
            save_membership = this.membership
            if this.membership:
                # Partner is a direct member
                if this.hierarchy_membership or this.associate_member:
                    super(ResPartner, this).write({
                        'associate_member': False,
                        'hierarchy_membership': False})
            else:
                # Might still be member through partner above
                for partner_above in this.partner_above_ids:
                    associate = partner_above.partner_above_id
                    # Only write real changes
                    if associate.membership and (
                            not this.membership or
                            this.associate_member != associate or
                            not this.hierarchy_membership):
                        super(ResPartner, this).write({
                            'membership': True,
                            'associate_member': associate.id,
                            'hierarchy_membership': True})
                        break
            if this.membership != save_membership:
                this.membership_change_trigger()

    hierarchy_membership = fields.Boolean(
        string='Membership through hierarchy',
        readonly=True)
