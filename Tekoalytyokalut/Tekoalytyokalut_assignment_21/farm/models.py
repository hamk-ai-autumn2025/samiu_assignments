from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
        ("potato", "Peruna"),
        ("carrot", "Porkkana"),
        ("other", "Muu juures"),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price_eur = models.DecimalField(max_digits=6, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_category_display()})"


class Service(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title
