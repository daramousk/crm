# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class ResPartnerRelation(models.Model):
    _inherit = 'res.partner.relation'

    @api.multi
    def _recompute_membership(self):
        import pdb
        pdb.set_trace()
        partner_model = self.env['res.partner']
        partners = partner_model.browse([])
        for this in self:
            partners = partners | this.left_partner_id | this.right_partner_id
        self.env.add_todo(partner_model._fields['membership'], partners)
        partner_model.recompute()

    @api.model
    def create(self, vals):
        result = super(ResPartnerRelation, self).create(vals)
        result._recompute_membership()
        return result

    @api.multi
    def write(self, vals):
        result = super(ResPartnerRelation, self).write(vals)
        self._recompute_membership()
        return result

    @api.multi
    def unlink(self):
        # For unlink must determine partners before call to super
        partner_model = self.env['res.partner']
        partners = partner_model.browse([])
        for this in self:
            partners = partners | this.left_partner_id | this.right_partner_id
        result = super(ResPartnerRelation, self).unlink()
        self.env.add_todo(partner_model._fields['membership'], partners)
        partner_model.recompute()
        return result
