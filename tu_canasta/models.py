from decimal import Decimal
from typing import Optional

from django.contrib.auth.hashers import is_password_usable, make_password
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum


class User(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'.strip() or self.email

    def set_password(self, raw_password: str) -> None:
        self.password = make_password(raw_password)

    def save(self, *args, **kwargs):
        # Ensure password stays hashed when saving via the ORM
        if not is_password_usable(self.password):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)


class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.sku})'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_lists',
    )
    title = models.CharField(max_length=255, default='Lista de compras')
    target_date = models.DateField(blank=True, null=True)
    budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-target_date', '-updated_at']

    def __str__(self):
        return f'{self.title} ({self.user})'

    @property
    def total_items(self) -> int:
        return self.items.count()

    @property
    def purchased_items(self) -> int:
        return self.items.filter(is_purchased=True).count()

    @property
    def pending_items(self) -> int:
        return self.total_items - self.purchased_items

    @property
    def total_cost(self) -> Decimal:
        aggregate = self.items.aggregate(
            total=Sum(
                F('quantity') * F('unit_price'),
                output_field=models.DecimalField(max_digits=12, decimal_places=2),
            )
        )
        return aggregate['total'] or Decimal('0.00')

    @property
    def total_spent(self) -> Decimal:
        aggregate = self.items.filter(is_purchased=True).aggregate(
            total=Sum(
                F('quantity') * F('unit_price'),
                output_field=models.DecimalField(max_digits=12, decimal_places=2),
            )
        )
        return aggregate['total'] or Decimal('0.00')

    @property
    def remaining_budget(self) -> Optional[Decimal]:
        if self.budget is None:
            return None
        return self.budget - self.total_cost


class ShoppingListItem(models.Model):
    shopping_list = models.ForeignKey(
        ShoppingList,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='shopping_list_items',
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        default=1,
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
    )
    is_purchased = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['shopping_list', 'product'],
                name='unique_product_per_shopping_list',
            )
        ]

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    @property
    def total_price(self) -> Decimal:
        return self.unit_price * self.quantity
