import unittest
from decimal import Decimal

from proteus import Model
from trytond.modules.company.tests.tools import create_company
from trytond.modules.product_variant.tests.tools import create_attributes
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules


class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):

        # Install product_cost_plan Module
        config = activate_modules('product_variant')

        # Create company
        _ = create_company()

        # Create attributes
        Attribute = Model.get('product.attribute')
        attributes = create_attributes()

        # Create product
        ProductUom = Model.get('product.uom')
        unit, = ProductUom.find([('name', '=', 'Unit')])
        ProductTemplate = Model.get('product.template')
        template = ProductTemplate()
        template.name = 'Tryton T-Shirt'
        template.default_uom = unit
        template.type = 'goods'
        template.list_price = Decimal('10')
        template.cost_price = Decimal('5')
        template.cost_price_method = 'fixed'
        template.code = '001-'
        attributes = Attribute.find()

        for attribute in attributes:
            template.attributes.append(attribute)

        template.save()
        ProductTemplate.generate_variants([template.id], config.context)

        self.assertEqual([(product.suffix_code, product.code)
                          for product in template.products], [('BL', '001-BL'),
                                                              ('BM', '001-BM'),
                                                              ('RL', '001-RL'),
                                                              ('RM', '001-RM')])
