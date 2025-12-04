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
    'version': '18.0.0.1.0',
    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product'],

    # always loaded
    'data': [
        'data/security.xml',
        'security/ir.model.access.csv',
        'views/product_product_view.xml',
    ],
    'application': False,

}
