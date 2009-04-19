#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields
from decimal import Decimal

class SaleLine(ModelSQL, ModelView):
    'Sale Line'
    _name = 'sale.line'
    _description = __doc__

    discount = fields.Numeric('Discount %', digits=(16, 2),
                              states={
                                  'invisible': "type != 'line'",
                                      })
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
        if vals.get('type') == 'line' and vals.get('discount'):
            vals = vals.copy()
            vals['unit_price'] = (vals.get('unit_price') -
                vals.get('unit_price') * vals.get('discount') * Decimal('0.01'))
        return super(SaleLine, self).on_change_with_amount(cursor, user,
                                                ids, vals, context=context)

    def get_amount(self, cursor, user, ids, name, arg, context=None):
        currency_obj = self.pool.get('currency.currency')
        res = super(SaleLine, self).get_amount(cursor, user, ids, name, arg,
                                                  context=context)
        for line in self.browse(cursor, user, ids, context=context):
            if line.type == 'line':
                currency = line.sale and line.sale.currency \
                        or line.currency
                res[line.id] = currency_obj.round(cursor, user, currency, \
                        Decimal(str(line.quantity)) * line.unit_price - \
                            (Decimal(str(line.quantity)) * line.unit_price *\
                            (line.discount * Decimal('0.01'))))
        return res

    def get_invoice_line(self, cursor, user, line, context=None):
        res = super(SaleLine, self).get_invoice_line(cursor, user, line,
                                                     context=context)[0]
        if line.type != 'line':
            return [res]
        if res['quantity'] <= 0.0:
            return None

        res['discount'] = line.discount
        return [res]

SaleLine()

class Sale(ModelSQL, ModelView):
    'Sale'
    _name = 'sale.sale'

    def on_change_lines(self, cursor, user, ids, vals, context=None):
        if vals.get('lines'):
            vals = vals.copy()
            lines = []
            for line in vals['lines']:
                if line.get('discount'):
                    line['unit_price'] = (line.get('unit_price')-
                              line.get('unit_price') * line.get('discount') *
                              Decimal('0.01'))
                lines.append(line)
            vals['lines'] = lines
        return super(Sale, self).on_change_lines(cursor, user, ids, vals,
                                                 context=context)

    def get_tax_amount(self, cursor, user, sales, context=None):
        '''
        Compute tax amount for each sales

        :param cursor: the database cursor
        :param user: the user id
        :param sales: a BrowseRecordList of sales
        :param context: the context
        :return: a dictionary with sale id as key and
            tax amount as value
        '''
        currency_obj = self.pool.get('currency.currency')
        tax_obj = self.pool.get('account.tax')
        if context is None:
            context = {}
        res = {}
        for sale in sales:
            ctx = context.copy()
            ctx.update(self.get_tax_context(cursor, user, sale,
                context=context))
            res.setdefault(sale.id, Decimal('0.0'))
            for line in sale.lines:
                if line.type != 'line':
                    continue
                price = line.unit_price - line.unit_price * line.discount / Decimal('100')
                # Don't round on each line to handle rounding error
                for tax in tax_obj.compute(cursor, user,
                        [t.id for t in line.taxes], price,
                        line.quantity, context=ctx):
                    res[sale.id] += tax['amount']
            res[sale.id] = currency_obj.round(cursor, user, sale.currency,
                    res[sale.id])
        return res

Sale()
