# This file is part product_variant module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import configuration
from . import product


def register():
    Pool.register(
        configuration.Configuration,
        configuration.ConfigurationCodeSeparator,
        product.Product,
        product.Template,
        product.ProductAttribute,
        product.AttributeValue,
        product.ProductTemplateAttribute,
        product.ProductAttributeValue,
        module='product_variant', type_='model')
