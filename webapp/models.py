from django.db import models

# Create your models here.
class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class CapHistoricReport(models.Model):
    plan = models.CharField(max_length=100)
    capmo = models.CharField(max_length=20)
    mbshp = models.IntegerField()

    class Meta:
        db_table = 'caphistoric_report_to_use_1year'  # Especificamos la tabla exacta en MySQL
        managed = False  # Evita que Django intente modificar la estructura de la tabla

    def __str__(self):
        return f"{self.plan} - {self.capmo} ({self.mbshp})"
