#This file is part sale_discount module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from decimal import Decimal
from trytond.model import fields
from trytond.pyson import Not, Equal, Eval
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction

__all__ = ['Sale', 'SaleLine']
__metaclass__ = PoolMeta


class Sale:
    'Sale'
    __name__ = 'sale.sale'

    def create_invoice(self, invoice_type):
        InvoiceLine = Pool().get('account.invoice.line')
        invoices = super(Sale, self).create_invoice(invoice_type)
        for line in self.lines:
            if line.discount != 0.0 and line.invoice_lines:
                InvoiceLine.write([line.invoice_lines[0]], {
                        'discount': line.discount,
                        })
        return invoices

    def create_shipment(self, shipment_type):
        Move = Pool().get('stock.move')
        shipments = super(Sale, self).create_shipment(shipment_type)
        for line in self.lines:
            if line.discount != 0.0 and line.moves:
                Move.write([line.moves[0]], {
                        'discount': line.discount,
                        })
        return shipments

    def get_tax_amount(self, name):
        '''
        Get taxes unit_price - discount
        '''
        pool = Pool()
        Tax = pool.get('account.tax')
        Invoice = pool.get('account.invoice')

        if (self.state in self._states_cached
                and self.tax_amount_cache is not None):
            return self.tax_amount_cache
        context = self.get_tax_context()
        taxes = {}
        for line in self.lines:
            if line.type != 'line':
                continue
            unit_price = line.unit_price
            if line.discount and line.discount is not None:
                unit_price =  unit_price - (
                    line.unit_price * (line.discount * Decimal('0.01')))
            with Transaction().set_context(context):
                tax_list = Tax.compute(line.taxes, unit_price,
                    line.quantity)
            # Don't round on each line to handle rounding error
            for tax in tax_list:
                key, val = Invoice._compute_tax(tax, 'out_invoice')
                if not key in taxes:
                    taxes[key] = val['amount']
                else:
                    taxes[key] += val['amount']
        amount = sum((self.currency.round(taxes[key]) for key in taxes),
            Decimal(0))
        return self.currency.round(amount)


class SaleLine:
    'Sale Line'
    __name__ = 'sale.line'

    discount = fields.Numeric('Discount %',
        digits=(16, Eval('currency_digits', 2)),
        states={
        'invisible': Not(Equal(Eval('type'), 'line')),
        }, on_change=['discount', 'product', 'quantity', 'type', 'unit_price'],
        depends=['type', 'unit_price', 'quantity', 'amount', 'currency_digits'])

    @staticmethod
    def default_discount():
        return Decimal(0.0)

    def on_change_discount(self):
        res = {}
        if self.quantity and self.discount and self.unit_price \
            and self.type == 'line':
            res['amount'] = Decimal(str(self.quantity)) * (self.unit_price - (
                self.unit_price * self.discount * Decimal('0.01')))
        return res

    def on_change_product(self):
        res = super(SaleLine, self).on_change_product()
        res['discount'] = Decimal(0.0)
        res['product_unit_price'] = self.on_change_with_product_unit_price()
        return res

    def on_change_quantity(self):
        res = super(SaleLine, self).on_change_quantity()
        res['discount'] = Decimal(0.0)
        return res

    def on_change_with_product_unit_price(self):
        if self.type == 'line' and self.product:
            Product = Pool().get('product.product')
            return Product.get_sale_price([self.product], 1)[self.product.id]
        return self.unit_price

    def get_amount(self, name):
        Currency = Pool().get('currency.currency')
        res = super(SaleLine, self).get_amount(name)
        if self.type == 'line' and self.discount and self.discount is not None:
            currency = self.sale and self.sale.currency \
                    or self.currency
            res = Currency.round(currency,
                Decimal(str(self.quantity)) * self.unit_price -
                (Decimal(str(self.quantity)) * self.unit_price *
                (self.discount * Decimal('0.01'))))
        return res
