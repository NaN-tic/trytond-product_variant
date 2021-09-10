# This file is part product_variant module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.

from trytond.pool import Pool, PoolMeta
from trytond.model import ModelView, ModelSQL, DeactivableMixin, fields
from trytond.pyson import Eval
from trytond.transaction import Transaction
from trytond import backend
import itertools


class Product(metaclass=PoolMeta):
    __name__ = 'product.product'
    attribute_values = fields.Many2Many('product.product-attribute.value',
        'product', 'value', 'Values', readonly=True,
        order=[('value.attribute.sequence', 'ASC')])

    @classmethod
    def __setup__(cls):
        super(Product, cls).__setup__()
        # order products by code ASC
        cls._order = [
            ('code', 'ASC'),
            ('id', 'DESC'),
            ]

    @classmethod
    def create(cls, vlist):
        for vals in vlist:
            if vals.get('template') and not vals['template']:
                vals = vals.copy()
                vals.pop('template')
        return super(Product, cls).create(vlist)


class Template(metaclass=PoolMeta):
    __name__ = 'product.template'
    attributes = fields.Many2Many('product.template-product.attribute',
        'template', 'attribute', 'Attributes',
        order=[('attribute.sequence', 'ASC')])
    variants = fields.Function(fields.Integer('Variants', select=1,
        help='Number variants from this template'),
        'get_variants', searcher='search_variants')

    @classmethod
    def __setup__(cls):
        super(Template, cls).__setup__()
        cls._buttons.update({
                'generate_variants': {
                    'invisible': Eval('template'),
                    }
                })

    @classmethod
    def __register__(cls, module_name):
        cursor = Transaction().connection.cursor()
        template = cls.__table__()

        table_h = backend.TableHandler(cls, module_name)
        code_exists = table_h.column_exist('code')
        super().__register__(module_name)
        if not code_exists:
            cursor.execute(*template.update(
                    columns=[template.code],
                    values=[template.basecode]))

    @classmethod
    def delete(cls, templates):
        #don't know - but this prevent always the deleation of the template
        #so the user has to delete empty templates manually
        templates = list(set(templates))
        if Transaction().delete:
            return templates
        return super(Template, cls).delete(templates)

    def get_variants(self, name=None):
        variants = len(self.products)
        if variants <= 1:
            variants = None
        return variants

    @classmethod
    def search_variants(cls, name, clause):
        res = []
        for template in cls.search([]):
            if len(template.products) >= clause[2]:
                res.append(template.id)
        return [('id', 'in', res)]

    @classmethod
    def create_variant_code(cls, variant):
        Config = Pool().get('product.configuration')
        config = Config(1)
        sep = config.code_separator or ''
        return sep.join(i.code for i in variant)

    def create_variant_product(self, variant):
        "Create the product from variant"
        pool = Pool()
        Product = pool.get('product.product')
        code = self.create_variant_code(variant)
        product, = Product.create([{
                    'template': self.id,
                    'suffix_code': code,
                    'attribute_values': [('add', [v.id for v in variant])],
                    }])
        return product

    def update_variant_product(self, products, variant):
        """Updates the code of supplied products with the code returned by
        create_code()"""
        pool = Pool()
        Product = pool.get('product.product')
        code = self.create_variant_code(variant)
        to_update = [p for p in products if p.code != code or not p.active]
        if to_update:
            Product.write(to_update, {
                    'suffix_code': code,
                    'active': True,
                    })

    def deactivate_variant_product(self, products):
        """Deactivates supplied products"""
        pool = Pool()
        Product = pool.get('product.product')
        to_update = [p for p in products if p.active]
        if to_update:
            Product.write(to_update, {
                    'active': False,
                    })

    @classmethod
    @ModelView.button
    def generate_variants(cls, templates):
        """Generate variants"""
        Product = Pool().get('product.product')
        for template in templates:
            if not template.attributes:
                continue
            all_template_products = Product.search([
                    ('template', '=', template.id),
                    ('active', 'in', (True, False)),
                    ])
            products_by_attr_values = {}
            to_deactivate = []
            for product in all_template_products:
                if (product.attribute_values
                        and all(v.active for v in product.attribute_values)):
                    key = tuple(
                        sorted(v.id for v in product.attribute_values))
                    products_by_attr_values.setdefault(key, []).append(
                        product)
                    continue
                to_deactivate.append(product)
            values = [a.values for a in template.attributes]
            for variant in itertools.product(*values):
                key = tuple(sorted(v.id for v in variant))
                if key in products_by_attr_values:
                    template.update_variant_product(
                        products_by_attr_values[key], variant)
                else:
                    template.create_variant_product(variant)
            template.deactivate_variant_product(to_deactivate)


class ProductAttribute(ModelSQL, ModelView):
    "Product Attribute"
    __name__ = "product.attribute"
    name = fields.Char('Name', required=True, translate=True)
    code = fields.Char('Code', required=True)
    sequence = fields.Integer('Sequence')
    values = fields.One2Many('product.attribute.value', 'attribute', 'Values')

    @classmethod
    def __setup__(cls):
        super(ProductAttribute, cls).__setup__()
        cls._order.insert(0, ('sequence', 'ASC'))

    @classmethod
    def __register__(cls, module_name):
        sql_table = cls.__table__()
        table_h = backend.TableHandler(cls, module_name)
        cursor = Transaction().connection.cursor()

        code_not_exists = not table_h.column_exist('code')

        super(ProductAttribute, cls).__register__(module_name)

        if code_not_exists:
            cursor.execute(*sql_table.update(
                    columns=[sql_table.code],
                    values=[sql_table.name]))

    @staticmethod
    def order_sequence(tables):
        table, _ = tables[None]
        return [table.sequence == None, table.sequence]


class AttributeValue(DeactivableMixin, ModelSQL, ModelView):
    "Values for Attributes"
    __name__ = "product.attribute.value"
    name = fields.Char('Name', required=True, translate=True)
    code = fields.Char('Code', required=True)
    sequence = fields.Integer('Sequence')
    attribute = fields.Many2One('product.attribute', 'Product Attribute',
        required=True, ondelete='CASCADE')

    @classmethod
    def __setup__(cls):
        super(AttributeValue, cls).__setup__()
        cls._order.insert(0, ('sequence', 'ASC'))

    @staticmethod
    def default_sequence():
        return 0

    @classmethod
    def deactivate(cls, values):
        """Deactivates products attribute values"""
        to_update = [p for p in values if p.active]
        if to_update:
            cls.write(to_update, {
                    'active': False,
                    })

    @classmethod
    def activate(cls, values):
        """Activates products attribute values"""
        to_update = [p for p in values if not p.active]
        if to_update:
            cls.write(to_update, {
                    'active': True,
                    })


class ProductTemplateAttribute(ModelSQL, ModelView):
    "Product Template - Product Attribute"
    __name__ = "product.template-product.attribute"
    attribute = fields.Many2One('product.attribute', 'Product Attribute',
            ondelete='RESTRICT', required=True)
    template = fields.Many2One('product.template', 'Product template',
            ondelete='CASCADE', required=True)

    @classmethod
    def __setup__(cls):
        super(ProductTemplateAttribute, cls).__setup__()
        cls._order.insert(0, ('attribute.sequence', 'ASC'))


class ProductAttributeValue(ModelSQL, ModelView):
    "Product - Product Attribute Value"
    __name__ = "product.product-attribute.value"
    product = fields.Many2One('product.product', 'Product',
            ondelete='CASCADE', required=True)
    value = fields.Many2One('product.attribute.value', 'Attribute Value',
            ondelete='CASCADE', required=True)

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._order.insert(0, ('value.attribute.sequence', 'ASC'))
