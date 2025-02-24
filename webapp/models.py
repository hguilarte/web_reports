from django.db import models

class CapHistoricReport(models.Model):
    center = models.CharField(max_length=100, db_column="CENTER")
    plan = models.CharField(max_length=100, db_column="PLAN")
    lob = models.CharField(max_length=50, db_column="LOB")
    mbshp = models.IntegerField(db_column="MBSHP")
    id = models.CharField(max_length=50, primary_key=True, db_column="ID")
    hic_num = models.CharField(max_length=50, db_column="HIC_NUM")
    mcaid_num = models.CharField(max_length=50, db_column="MCAID_NUM")
    membname = models.CharField(max_length=200, db_column="MEMBNAME")
    dob = models.DateField(db_column="DOB")
    age = models.IntegerField(db_column="AGE")
    sex = models.CharField(max_length=1, db_column="SEX")
    address = models.CharField(max_length=255, db_column="ADDRESS")
    city = models.CharField(max_length=100, db_column="CITY")
    st = models.CharField(max_length=2, db_column="ST")
    zip = models.CharField(max_length=10, db_column="ZIP")
    county = models.CharField(max_length=100, db_column="COUNTY")
    phonenumber = models.CharField(max_length=20, db_column="PHONENUMBER")
    capmo = models.CharField(max_length=20, db_column="CAPMO")
    pcpname = models.CharField(max_length=255, db_column="PCPNAME")

    class Meta:
        db_table = 'caphistoric_report_to_use'  # Asegura que el nombre es correcto
        managed = False  # Evita que Django intente modificar la tabla

    def __str__(self):
        return f"{self.center} - {self.plan} - {self.capmo} - {self.mbshp}"
