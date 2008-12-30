#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
{
    'name': 'Sale Order Discount',
    'name_de_DE': 'Rabattspalte für Angebot/Auftrag',
    'version': '0.0.1',
    'author': 'virtual things',
    'email': 'info@virtual-things.biz',
    'website': 'http://www.virtual-things.biz/',
    'description': '''This module adds a discount column on sale order
''',
    'description_de_DE': '''Dieses Modul fügt dem Angebots- und Auftragsformular eine
    Rabattspalte hinzu
''',
    'depends': [
        'sale',
        'account_invoice_discount'
        ],
    'xml': [
        'sale.xml'
        ],
#    'translation': [
#        'de_DE.csv'
#    ],
}
