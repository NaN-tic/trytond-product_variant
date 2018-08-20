# This file is part of the product_variant module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from proteus import Model

_ATTRIBUTES = [{
    'name': 'Colors',
    'options': {
        'Red': 'R',
        'Black': 'B',
        },
    }, {
    'name': 'Sizes',
    'options': {
        'Large': 'L',
        'Medium': 'M',
        },
    }]

def create_attributes():
    "Create attributes"
    Attribute = Model.get('product.attribute')
    AttributeValue = Model.get('product.attribute.value')

    attributes = []
    for a in _ATTRIBUTES:
        attribute = Attribute()
        attribute.name = a['name']
        attribute.code = a['name'].lower()
        for k, v in a['options'].items():
            value = AttributeValue()
            value.name = k
            value.code = v
            attribute.values.append(value)
        attribute.save()
        attributes.append(attribute)
    return attributes
