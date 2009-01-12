#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
{
    'name': 'Sales Discount',
    'name_de_DE': 'Verkauf Rabatt',
    'version': '0.0.1',
    'author': 'virtual things',
    'email': 'info@virtual-things.biz',
    'website': 'http://www.virtual-things.biz/',
    'description': '''Define discounts for sale lines
    - with additional field discount in report sale
''',
    'description_de_DE': '''Ermöglicht die Eingabe von Rabatten pro Verkaufsposition
    - mit zusätzlichem Rabattfeld im Bericht Verkauf
''',
    'depends': [
        'sale',
        'account_invoice_discount'
        ],
    'xml': [
        'sale.xml'
        ],
    'translation': [
        'de_DE.csv'
    ],
}
