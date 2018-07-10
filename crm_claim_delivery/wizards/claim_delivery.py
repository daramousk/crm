# -*- coding: utf-8 -*-
# Copyright 2017-2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class ClaimDeliveryWizard(models.TransientModel):
    _name = "crm.delivery_wizard"
    _description = "wizard choose products"

    claim_id = fields.Many2one(
        'crm.claim',
        string="Claim")
    delivery_id = fields.Many2one(
        'stock.picking',
        string="Delivery")
    product_id = fields.Many2one(
        "product.template",
        string="product",
        domain=lambda self: [("id", "in", self.get_products())])

    @api.multi
    def get_products(self):
        if self.env.context.get("active_ids", False):
            products = []
            claimID = self.env.context.get("active_ids", False)[0]
            claim = self.env['crm.claim'].browse(claimID)
            delivery = claim.delivery_id
            pack_products = delivery.mapped(
                'pack_operation_ids.product_id')
            move_products = delivery.mapped(
                'move_lines.product_id')
            products = pack_products | move_products
            return products.mapped('product_tmpl_id').ids
        return []

    @api.model
    def default_get(self, fields_list):
        res = {}
        res = super(ClaimDeliveryWizard, self).default_get(
            fields_list=fields_list)
        claim_model = self.env['crm.claim']
        claimID = self.env.context.get("active_ids", False)
        if claimID:
            claim = claim_model.browse(claimID[0])
            res['claim_id'] = claim.id
            self.write({'claim_id': claim.id})
            res['delivery_id'] = claim.delivery_id.id
        return res

    @api.multi
    def save(self):
        self.claim_id.write({
            'product_selected_ids': [(4, self.product_id.id)]})
        return True
