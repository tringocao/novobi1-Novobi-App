{
    'name': 'Lunch Order',
    'version': '1.0',
    'summary': 'Sell something',
    'category': 'Tools',
    'description':
        """
        Novobi Internship: Lunch Service 
        """,
    'data': [
        "views/home.xml",
        "views/foods_view.xml",
        "views/layout.xml",
        "views/modal.xml",
        "views/food_img.xml",
        "views/lunch_confirm.xml",
        "views/slack_name.xml",
        "views/day_menu.xml",
        "views/foody.xml",
        "views/foody_product.xml",
        "security/ir.model.access.csv",
        "data/demo_data.xml",
        "views/reports_view.xml",
        "views/invite_data.xml",
        "views/scheduler.xml",

    ],
    'depends': ['sale_stock', 'auth_signup', 'website_sale','product','project','payment','sale','lunch','website' ],
    'qweb': ['static/src/xml/*.xml'],
    'application': True,
}
