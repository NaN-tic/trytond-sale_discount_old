#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
{
    'name': 'Sale Discount',
    'name_ca_ES': 'Descomptes comandes de venda',
    'name_de_DE': 'Verkauf Rabatt',
    'name_es_ES': 'Descuentos pedidos de venta',
    'version': '2.4.0',
    'author': 'virtual things',
    'email': 'info@virtual-things.biz',
    'website': 'http://www.virtual-things.biz/',
    'description': '''Discounts for Sales
    - Define discounts for sale lines
    - Adds field discount in report sale
''',
    'description_ca_ES': '''Descomptes per a vendes
    - Defineix descomptes per a línies de venda
    - Afegeix camp descompte al tiquet de venda
''',
    'description_de_DE': '''Rabatt für Verkäufe
    - Ermöglicht die Eingabe von Rabatten pro Verkaufsposition
    - Fügt Rabattfeld im Bericht Verkauf hinzu
''',
    'description_es_ES': '''Descuentos para ventas
    - Define descuentos para líneas de ventas
    - Añade campo descuento al tiquet de venta
''',
    'depends': [
        'sale',
        'account_invoice_discount',
        ],
    'xml': [
        'move.xml',
        'sale.xml',
        ],
    'translation': [
        'locale/ca_ES.po',
        'locale/de_DE.po',
        'locale/es_ES.po',
    ],
}
