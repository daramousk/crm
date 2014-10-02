#-*- coding: utf-8 -*-
'''Extend publication.publication model'''
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm, fields


class Publication(orm.Model):
    '''Publication information'''
    _name = 'publication.publication'

    _columns = {
        'code': fields.char('Code', size=16, required=True),
        'name': fields.char('Name', size=64, required=True),
        'email_distribution': fields.boolean('Can be send by email'),
        'print_distribution': fields.boolean('Can be send in print'),
        'date_start': fields.date('Date start'),
        'date_end': fields.date('Date end'),
    }                                                                          

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4