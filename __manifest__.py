# -*- coding: utf-8 -*-
{
    'name': "Padron de Impuestos Santa Fe",

    'summary': """
        Módulo para gestionar el padrón de impuestos de la provincia de Santa Fe.""",

    'description': """
        Este módulo permite gestionar el padrón de impuestos de la provincia de Santa Fe, incluyendo la validación de clientes y la asignación automática de impuestos en las órdenes de venta y pagos.
    """,

    'author': "GonzaOdoo",
    'website': "https://github.com/GonzaOdoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['sale','base','account','l10n_ar_account_withholding'],

    'data':[
        'security/ir.model.access.csv',
        'views/partner_tax_padron_views.xml',
        'views/import_wizard_views.xml',
    ]

}