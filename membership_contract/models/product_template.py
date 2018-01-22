# -*- coding: utf-8 -*-
# Copyright 2014-2017 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    membership = fields.Boolean(string='Product is a membership?')
    membership_pricelist = fields.Many2one(
        comodel_name='product.pricelist',
        string='Membership pricelist',
        help="Used to register special prices and rebates for members")
