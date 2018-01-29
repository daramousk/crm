# -*- coding: utf-8 -*-
# Copyright 2014-2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    membership = fields.Boolean(string='Product is a membership?')
    membership_pricelist = fields.Many2one(
        comodel_name='product.pricelist',
        string='Membership pricelist',
        help="Used to register special prices and rebates for members")

    @api.multi
    def membership_change_trigger(self):
        """Postprocess records immediately after changing membership field.

        Make sure membership correctly set on contract lines.
        """
        line_model = self.env['account.analytic.invoice.line']
        for this in self:
            lines = line_model.search([
                ('product_id.product_tmpl_id', '=', this.id)])
            for line in lines:
                if line.membership != this.membership:
                    line.write({'membership': this.membership})

    @api.multi
    def write(self, vals):
        if not 'membership' in vals:
            return super(ProductTemplate, self).write(vals)
        for this in self:
            save_membership = this.membership
            super(ProductTemplate, this).write(vals)
            if this.membership != save_membership:
                this.membership_change_trigger()
        return True
