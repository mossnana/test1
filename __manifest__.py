# -*- coding: utf-8 -*-
{
    'name': "AC Order",

    'summary': """
        This is test 1 from Odoo 
        Develop by Permpoon
                """,

    'description': """
        For Support to Developer, Give me a star @ github.com/mossnana
    """,

    'author': "Permpoon Chaowanaphunphon",
    'website': "https://mossnana.github.io/resume",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/wizard_view.xml',
        'report/report_ac_order.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}
