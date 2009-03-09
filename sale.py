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
        currency_obj = self.pool.get('currency.currency')
        if vals.get('type') == 'line':
            if isinstance(vals.get('_parent_sale.currency'), (int, long)):
                currency = currency_obj.browse(cursor, user,
                        vals['_parent_sale.currency'], context=context)
            else:
                currency = vals['_parent_sale.currency']
            discount = Decimal(str(vals.get('quantity') or Decimal('0.0'))) * \
                         (vals.get('unit_price') or Decimal('0.0')) * \
                         (((Decimal(vals.get('discount') or '0.0') * \
                         Decimal('0.01'))) or Decimal('0.0'))
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
                for line2 in line.sale.lines:
                    if line2.type == 'line':
                        res[line.id] += currency_obj.round(cursor, user, \
                            line2.sale.currency, \
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

    def get_invoice_line(self, cursor, user, line, context=None):
        '''
        Return invoice line values for sale line

        :param cursor: the database cursor
        :param user: the user id
        :param line: the BrowseRecord of the line
        :param context: the context

        :return: a list of invoice line values
        '''
        uom_obj = self.pool.get('product.uom')
        property_obj = self.pool.get('ir.property')

        res = {}
        res['sequence'] = line.sequence
        res['type'] = line.type
        res['description'] = line.description
        if line.type != 'line':
            return [res]
        if line.sale.invoice_method == 'order':
            res['quantity'] = line.quantity
        else:
            quantity = 0.0
            for move in line.moves:
                if move.state == 'done':
                    quantity += uom_obj.compute_qty(cursor, user, move.uom,
                            move.quantity, line.unit, context=context)
            for invoice_line in line.invoice_lines:
                quantity -= uom_obj.compute_qty(cursor, user,
                        invoice_line.unit, invoice_line.quantity, line.unit,
                        context=context)
            res['quantity'] = quantity
        if res['quantity'] <= 0.0:
            return None
        res['unit'] = line.unit.id
        res['product'] = line.product.id
        res['unit_price'] = line.unit_price
        res['discount'] = line.discount
        res['taxes'] = [('set', [x.id for x in line.taxes])]
        if line.product:
            res['account'] = line.product.account_revenue_used.id
        else:
            for model in ('product.template', 'product.category'):
                res['account'] = property_obj.get(cursor, user,
                        'account_revenue', model, context=context)
                if res['account']:
                    break
            if not res['account']:
                self.raise_user_error(cursor, 'missing_account_revenue',
                        context=context)
        return [res]

SaleLine()

class Sale(ModelSQL, ModelView):
    'Sale'
    _name = 'sale.sale'

    def on_change_lines(self, cursor, user, ids, vals, context=None):
        currency_obj = self.pool.get('currency.currency')
        tax_obj = self.pool.get('account.tax')

        if context is None:
            context = {}

        res = {
            'untaxed_amount': Decimal('0.0'),
            'tax_amount': Decimal('0.0'),
            'total_amount': Decimal('0.0'),
        }

        currency = None
        if vals.get('currency'):
            currency = currency_obj.browse(cursor, user, vals['currency'],
                    context=context)

        if vals.get('lines'):
            ctx = context.copy()
            ctx.update(self.get_tax_context(cursor, user, vals,
                context=context))
            for line in vals['lines']:
                if line.get('type', 'line') != 'line':
                    continue
                res['untaxed_amount'] += line.get('amount', Decimal('0.0'))
                price = line.get('unit_price') - line.get('unit_price') * line.get('discount') / Decimal('100')
                for tax in tax_obj.compute(cursor, user, line.get('taxes', []),
                        price,
                        line.get('quantity', 0.0), context=context):
                    res['tax_amount'] += tax['amount']
        if currency:
            res['untaxed_amount'] = currency_obj.round(cursor, user, currency,
                    res['untaxed_amount'])
            res['tax_amount'] = currency_obj.round(cursor, user, currency,
                    res['tax_amount'])
        res['total_amount'] = res['untaxed_amount'] + res['tax_amount']
        if currency:
            res['total_amount'] = currency_obj.round(cursor, user, currency,
                    res['total_amount'])
        return res

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
