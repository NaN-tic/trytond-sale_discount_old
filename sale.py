#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import copy
from decimal import Decimal
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Not, Equal, Eval
from trytond.transaction import Transaction
from trytond.pool import Pool


class SaleLine(ModelSQL, ModelView):
    _name = 'sale.line'

    discount = fields.Numeric('Discount %', digits=(16, 2), states={
                'invisible': Not(Equal(Eval('type'), 'line')),
            }, depends=['type'])

    def __init__(self):
        super(SaleLine, self).__init__()
        self.amount = copy.copy(self.amount)
        if self.amount.on_change_with:
            self.amount.on_change_with.extend(['discount'])
        self._reset_columns()

    def default_discount(self):
        return 0.0

    def on_change_with_amount(self, vals):
        if vals.get('type') == 'line' and vals.get('unit_price') and \
         vals.get('discount'):
            vals = vals.copy()
            vals['unit_price'] = (vals.get('unit_price') -
                vals.get('unit_price') * vals.get('discount') * Decimal('0.01'))
        return super(SaleLine, self).on_change_with_amount(vals)

    def get_amount(self, ids, name):
        currency_obj = Pool().get('currency.currency')
        res = super(SaleLine, self).get_amount(ids, name)
        for line in self.browse(ids):
            if line.type == 'line':
                currency = line.sale and line.sale.currency \
                        or line.currency
                res[line.id] = currency_obj.round(currency,
                        Decimal(str(line.quantity)) * line.unit_price -
                            (Decimal(str(line.quantity)) * line.unit_price *
                            (line.discount * Decimal('0.01'))))
        return res

    def get_invoice_line(self, line, invoice_type):
        res = super(SaleLine, self).get_invoice_line(line, invoice_type)
        if not res:
            return []
        if line.type != 'line':
            return [res[0]]
        if res[0]['quantity'] <= 0.0:
            return None
        res[0]['discount'] = line.discount
        return [res[0]]

    def get_move(self, line, shipment_type):
        '''
        Add discount value in move out for the sale line
        '''
        res = super(SaleLine, self).get_move(line, shipment_type)
        if line.discount and shipment_type == 'out':
            res['discount'] = line.discount
        return res

SaleLine()

class Sale(ModelSQL, ModelView):
    _name = 'sale.sale'

    def on_change_lines(self, vals):
        if vals.get('lines'):
            vals = vals.copy()
            lines = []
            for line in vals['lines']:
                if line.get('unit_price') and line.get('discount'):
                    line['unit_price'] = (line.get('unit_price')-
                              line.get('unit_price') * line.get('discount') *
                              Decimal('0.01'))
                lines.append(line)
            vals['lines'] = lines
        return super(Sale, self).on_change_lines(vals)

    def get_tax_amount(self, ids, name):
        '''
        Compute tax amount for each sales

        :param sales: a BrowseRecordList of sales
        :return: a dictionary with sale id as key and
            tax amount as value
        '''
        currency_obj = Pool().get('currency.currency')
        tax_obj = Pool().get('account.tax')
        res = {}
        for sale in self.browse(ids):
            context = self.get_tax_context(sale)
            res.setdefault(sale.id, Decimal('0.0'))
            for line in sale.lines:
                if line.type != 'line':
                    continue
                price = line.unit_price - line.unit_price * line.discount / Decimal('100')
                # Don't round on each line to handle rounding error
                with Transaction().set_context(**context):
                    taxes_compute = tax_obj.compute(
                            [t.id for t in line.taxes], price, line.quantity)

                for tax in taxes_compute:
                    res[sale.id] += tax['amount']
            res[sale.id] = currency_obj.round(sale.currency, res[sale.id])
        return res

Sale()
