========================
Product Variant Scenario
========================

Imports::

    >>> from decimal import Decimal
    >>> from proteus import config, Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.product_variant.tests.tools import create_attributes

Install product_cost_plan Module::

    >>> config = activate_modules('product_variant')

Create attributes::

    >>> Attribute = Model.get('product.attribute')
    >>> attributes = create_attributes()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> ProductTemplate = Model.get('product.template')
    >>> template = ProductTemplate()
    >>> template.name = 'Tryton T-Shirt'
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.list_price = Decimal('10')
    >>> template.cost_price = Decimal('5')
    >>> template.cost_price_method = 'fixed'
    >>> template.basecode = '001-'
    >>> attributes = Attribute.find()
    >>> for attribute in attributes:
    ...     template.attributes.append(attribute)
    >>> template.save()
    >>> ProductTemplate.generate_variants([template.id], config.context)
    >>> Product = Model.get('product.product')
    >>> product, = Product.find([('code', '=', '001-RL')])
    >>> product.code
    '001-RL'
