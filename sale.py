#This file is part sale_discount module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.
from decimal import Decimal
from trytond.model import fields
from trytond.pyson import Not, Equal, Eval
from trytond.pool import Pool, PoolMeta

__all__ = ['SaleLine']
__metaclass__ = PoolMeta

class SaleLine:
    'Sale Line'
    __name__ = 'sale.line'

    discount = fields.Numeric('Discount %', 
        digits=(16, Eval('currency_digits', 2)), 
        states={
        'invisible': Not(Equal(Eval('type'), 'line')),
        }, on_change=['discount', 'product', 'quantity', 'type', 'unit_price'],
        depends=['type','unit_price', 'quantity', 'amount'])

    @staticmethod
    def default_discount():
        return Decimal(0.0)

    def on_change_discount(self):
        res = {}
        if self.discount == Decimal(0.0) and self.quantity != None:
            res['amount'] = Decimal(self.quantity)*self.unit_price
        if self.discount and self.unit_price and self.type == 'line':
            res['amount'] = Decimal(self.quantity)*(self.unit_price -
                self.unit_price * self.discount * Decimal('0.01'))
        return res

    def on_change_product(self):
        res = super(SaleLine, self).on_change_product()
        res['discount'] = Decimal(0.0)
        return res

    def on_change_quantity(self):
        res = super(SaleLine, self).on_change_quantity()
        res['discount'] = Decimal(0.0)
        return res

    def get_amount(self, name):
        Currency = Pool().get('currency.currency')
        res = super(SaleLine, self).get_amount(name)
        if self.type == 'line' and self.discount and self.discount != None:
            currency = self.sale and self.sale.currency \
                    or self.currency
            res = Currency.round(currency, \
                    Decimal(str(self.quantity)) * self.unit_price - \
                        (Decimal(str(self.quantity)) * self.unit_price *\
                        (self.discount * Decimal('0.01'))))
        return res
 
