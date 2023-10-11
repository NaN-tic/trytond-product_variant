# This file is part product_variant module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields, ModelSQL, ModelSingleton, ModelView
from trytond.model import ValueMixin
from trytond.modules.company.model import CompanyMultiValueMixin

code_separator = fields.Char('Code Separator')


class Configuration(
        ModelSingleton, ModelSQL, ModelView, CompanyMultiValueMixin):
    __name__ = 'product.configuration'
    code_separator = fields.MultiValue(code_separator)


class ConfigurationCodeSeparator(ModelSQL, ValueMixin):
    'Product Configuration Code Separator'
    __name__ = 'product.configuration.code_separator'
    code_separator = code_separator
    _configuration_value_field = 'code_separator'

    @classmethod
    def default_code_separator(cls):
        return '-'
