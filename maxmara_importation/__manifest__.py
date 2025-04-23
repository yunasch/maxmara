# -*- coding: utf-8 -*-
{
    'name': "Max Mara Importation",

    'summary': """
        Max Mara Importation
    """,

    'description': """
        Max Mara Importation
        
    """,

    'author': "BDR Informática y Comunicaciones S.L.",
    'website': "https://www.bdrinformatica.com",


    'category': 'API',
    'version': '17.0.0.0',
    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product'],

    # always loaded
    'data': [
        'views/product_product_view.xml',
    ],
    'application': False,

}
