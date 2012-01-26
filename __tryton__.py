#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
{
    'name': 'Sale Discount',
    'name_de_DE': 'Verkauf Rabatt',
    'version': '2.1.2',
    'author': 'virtual things',
    'email': 'info@virtual-things.biz',
    'website': 'http://www.virtual-things.biz/',
    'description': '''Discounts for Sales
    - Define discounts for sale lines
    - Adds field discount in report sale
''',
    'description_de_DE': '''Rabatt für Verkäufe
    - Ermöglicht die Eingabe von Rabatten pro Verkaufsposition
    - Fügt Rabattfeld im Bericht Verkauf hinzu
''',
    'depends': [
        'sale',
        'account_invoice_discount'
        ],
    'xml': [
        'sale.xml'
        ],
    'translation': [
        'locale/de_DE.po'
    ],
}
