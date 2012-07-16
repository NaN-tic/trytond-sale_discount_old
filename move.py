#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from decimal import Decimal
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Not, Equal, Eval
from trytond.transaction import Transaction
from trytond.pool import Pool

class Move(ModelSQL, ModelView):
    _name = 'stock.move'

    discount = fields.Numeric('Discount %', digits=(16, 4),
        states={
            'readonly': Not(Equal(Eval('state'), 'draft')),
            },
        depends=['state'])

Move()
