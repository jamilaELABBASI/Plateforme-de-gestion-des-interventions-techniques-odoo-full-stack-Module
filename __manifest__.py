{
    'name': "intervention_management",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "Jamila ELABBASI",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Jamila EL ABBASI',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    'assets': {
        'web.assets_backend': [
            'intervention_management/static/src/css/intervention.css',
        ],
    },

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/intervention/intervention_search.xml',
        'views/intervention/intervention_actions.xml',
        'views/intervention/intervention.xml',
        'views/technicien/technicien.xml',
        'views/technicien/technicien_actions.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
    'application': True,

}

