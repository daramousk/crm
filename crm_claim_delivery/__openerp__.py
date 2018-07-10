# -*- coding: utf-8 -*-
# Copyright 2017-2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Claims for deliveries",
    "version": "8.0.1.0.0",
    "author": "Therp BV",
    "license": "AGPL-3",
    "category": "Customer Relationship Management",
    "summary": "Claim connected to deliveries",
    "depends": [
        'stock',
        'crm_claim_type'
    ],
    "data": [
        'data/crm_claim_type.xml',
        'wizards/claim_delivery.xml',
        'views/crm_claim.xml',
        'views/product_template.xml',
    ],
    "installable": True,
}
