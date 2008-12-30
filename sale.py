#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.osv import fields, OSV
from decimal import Decimal

class SaleLine(OSV):
    'Sale Line'
    _name = 'sale.line'
    _description = __doc__
    
    discount = fields.Numeric('Discount %', digits=(16, 2))
    amount = fields.Function('get_amount', type='numeric', string='Amount',
            digits="(16, _parent_sale.currency_digits)",
            states={
                'invisible': "type not in ('line', 'subtotal')",
                'readonly': "not globals().get('_parent_sale')",
            }, on_change_with=['type', 'quantity', 'unit_price',
                '_parent_sale.currency','discount'])
    
    def default_discount(self, cursor, user, context=None):
        return 0.0
    
    def on_change_with_amount(self, cursor, user, ids, vals, context=None):
        currency_obj = self.pool.get('currency.currency')
        if vals.get('type') == 'line':
            if isinstance(vals.get('_parent_sale.currency'), (int, long)):
                currency = currency_obj.browse(cursor, user,
                        vals['_parent_sale.currency'], context=context)
            else:
                currency = vals['_parent_sale.currency']
            discount = Decimal(str(vals.get('quantity') or Decimal('0.0'))) * \
                         (vals.get('unit_price') or Decimal('0.0')) * \
                         (((vals.get('discount')* Decimal('0.01'))) or \
                          Decimal('0.0'))
            amount = Decimal(str(vals.get('quantity') or '0.0')) * \
                    (vals.get('unit_price') or Decimal('0.0')) - discount
            if currency:
                return currency_obj.round(cursor, user, currency, amount)
            return amount
        return Decimal('0.0')
    
    def get_amount(self, cursor, user, ids, name, arg, context=None):
        currency_obj = self.pool.get('currency.currency')
        res = {}
        for line in self.browse(cursor, user, ids, context=context):
            if line.type == 'line':
                currency = line.sale and line.sale.currency \
                        or line.currency
                res[line.id] = currency_obj.round(cursor, user, currency, \
                        Decimal(str(line.quantity)) * line.unit_price - \
                            (Decimal(str(line.quantity)) * line.unit_price *\
                            (line.discount * Decimal('0.01'))))
            elif line.type == 'subtotal':
                res[line.id] = Decimal('0.0')
                for line2 in line.invoice.lines:
                    if line2.type == 'line':
                        res[line.id] += currency_obj.round(cursor, user, \
                            line2.invoice.currency, \
                            Decimal(str(line2.quantity)) * line2.unit_price - \
                            (Decimal(str(line2.quantity)) * line2.unit_price *\
                            (line2.discount * Decimal('0.01'))))
                        print res[line.id]
                    elif line2.type == 'subtotal':
                        if line.id == line2.id:
                            break
                        res[line.id] = Decimal('0.0')
            else:
                res[line.id] = Decimal('0.0')
        return res
    
SaleLine()