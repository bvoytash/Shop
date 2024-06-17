from django.db import models


class Product(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title


class Order(models.Model):
    date = models.DateField()
    products = models.ManyToManyField(Product)

    def __str__(self):
        return f"Order {self.id} on {self.date}"
