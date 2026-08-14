from django.db import models


class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name="Назва товару")
    color = models.CharField(max_length=100, blank=True, null=True, verbose_name="Колір")
    storage = models.CharField(max_length=100, blank=True, null=True, verbose_name="Вбудована пам'ять")
    product_code = models.CharField(max_length=100, blank=True, null=True, verbose_name="Код товару")
    reviews = models.IntegerField(blank=True, null=True, verbose_name="Кількість рецензій")
    screen_diagonal = models.CharField(max_length=100, blank=True, null=True, verbose_name="Діагональ екрану")
    display_resolution = models.CharField(max_length=100, blank=True, null=True, verbose_name="Роздільна здатність екрану")
    photos = models.JSONField(default=list, blank=True, verbose_name="Фотографії")
    characteristics = models.JSONField(default=dict, blank=True, verbose_name="Характеристики")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"

    def __str__(self):
        return self.title
