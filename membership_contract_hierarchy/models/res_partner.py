# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends(
        'membership_line_ids',
        'partner_above_ids')
    def _compute_membership(self):
        for this in self:
            super(ResPartner, this)._compute_membership()
            if not this.membership:
                # Might still be member through partner above
                for partner_above in this.partner_above_ids:
                    if partner_above.membership:
                        this.membership = True
                        break
