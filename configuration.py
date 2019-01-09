# This file is part product_variant module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields, ModelSQL, ModelSingleton, ModelView
from trytond.pool import PoolMeta
from trytond import backend
from trytond.model import ValueMixin
from trytond.tools.multivalue import migrate_property
from trytond.modules.company.model import CompanyMultiValueMixin

__all__ = ['Configuration','ConfigurationCodeSeparator']
__metaclass__ = PoolMeta


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
    def __register__(cls, module_name):
        TableHandler = backend.get('TableHandler')
        exist = TableHandler.table_exist(cls._table)

        super(ConfigurationCodeSeparator, cls).__register__(
            module_name)

        if not exist:
            cls._migrate_property([], [], [])

    @classmethod
    def _migrate_property(cls, field_names, value_names, fields):
        field_names.append('default_default_code_separator')
        value_names.append('default_default_code_separator')
        migrate_property(
            'product.configuration', field_names, cls, value_names,
            fields=fields)

    @classmethod
    def default_default_code_separator(cls):
        return '-'
