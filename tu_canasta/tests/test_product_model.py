from django.test import TestCase
from tu_canasta.models import Product
from django.db import IntegrityError

class ProductModelTest(TestCase):

    def setUp(self):
        self.product = Product.objects.create(
            sku="SKU123",
            name="Café de Colombia",
            description="Café suave y aromático."
        )

    def test_product_creation(self):
        """Debe crear un producto con los campos correctos"""
        self.assertEqual(self.product.sku, "SKU123")
        self.assertEqual(self.product.name, "Café de Colombia")
        self.assertTrue(isinstance(self.product, Product))
        self.assertIsNotNone(self.product.created_at)

    def test_str_representation(self):
        """El método __str__ debe devolver el formato correcto"""
        self.assertEqual(str(self.product), "Café de Colombia (SKU123)")

    def test_unique_sku_constraint(self):
        """No debe permitir duplicar el SKU"""
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                sku="SKU123",  # igual al anterior
                name="Otro café",
                description="Café duplicado"
            )
