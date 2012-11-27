#This file is part sale_discount module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.model import fields
from trytond.pyson import Not, Equal, Eval
from trytond.pool import PoolMeta

__all__ = ['Move']
__metaclass__ = PoolMeta


class Move:
    "Stock Move"
    __name__ = 'stock.move'

    discount = fields.Numeric('Discount %', digits=(16, 4),
        states={
            'readonly': Not(Equal(Eval('state'), 'draft')),
            },
        depends=['state'])

