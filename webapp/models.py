from django.db import models

class CapHistoricReport(models.Model):
    """
    ✅ Model representing historic membership report data.
    This model is mapped to an existing database table (`caphistoric_report_to_use`) and is not managed by Django.
    """
    center = models.CharField(max_length=100, db_column="CENTER", db_index=True)
    plan = models.CharField(max_length=100, db_column="PLAN", db_index=True)
    lob = models.CharField(max_length=50, db_column="LOB")
    mbshp = models.IntegerField(db_column="MBSHP")
    id = models.CharField(max_length=50, primary_key=True, db_column="ID")
    hic_num = models.CharField(max_length=50, db_column="HIC_NUM")
    mcaid_num = models.CharField(max_length=50, db_column="MCAID_NUM")
    membname = models.CharField(max_length=200, db_column="MEMBNAME")
    dob = models.DateField(db_column="DOB", db_index=True)
    age = models.IntegerField(db_column="AGE")
    sex = models.CharField(max_length=1, db_column="SEX")
    address = models.CharField(max_length=255, db_column="ADDRESS")
    city = models.CharField(max_length=100, db_column="CITY")
    st = models.CharField(max_length=2, db_column="ST")
    zip = models.CharField(max_length=10, db_column="ZIP")
    county = models.CharField(max_length=100, db_column="COUNTY")
    phonenumber = models.CharField(max_length=20, db_column="PHONENUMBER")
    capmo = models.CharField(max_length=20, db_column="CAPMO", db_index=True)
    pcpname = models.CharField(max_length=255, db_column="PCPNAME")
    # Añadir el campo stat
    stat = models.CharField(max_length=50, db_column="STAT", null=True, blank=True)

    class Meta:
        db_table = 'caphistoric_report_to_use'  # ✅ Ensure the correct table mapping
        managed = False  # ✅ Prevent Django from modifying this table
        indexes = [
            models.Index(fields=['capmo']),
            models.Index(fields=['dob']),
            models.Index(fields=['plan']),
            models.Index(fields=['center']),
        ]

    def __str__(self):
        """
        ✅ String representation of the model instance.
        """
        return f"{self.center} - {self.plan} - {self.capmo} - {self.mbshp}"

class CapHistoricReportOneYear(models.Model):
    """
    ✅ Model representing one year historic membership report data with status information.
    This model is mapped to the existing database table (`webreports.caphistoric_report_to_use_1year`) and is not managed by Django.
    """
    center = models.CharField(max_length=100, db_column="CENTER", db_index=True)
    plan = models.CharField(max_length=100, db_column="PLAN", db_index=True)
    lob = models.CharField(max_length=50, db_column="LOB")
    mbshp = models.IntegerField(db_column="MBSHP")
    id = models.CharField(max_length=50, primary_key=True, db_column="ID")
    hic_num = models.CharField(max_length=50, db_column="HIC_NUM")
    mcaid_num = models.CharField(max_length=50, db_column="MCAID_NUM")
    membname = models.CharField(max_length=200, db_column="MEMBNAME")
    dob = models.DateField(db_column="DOB", db_index=True)
    age = models.IntegerField(db_column="AGE")
    sex = models.CharField(max_length=1, db_column="SEX")
    address = models.CharField(max_length=255, db_column="ADDRESS")
    city = models.CharField(max_length=100, db_column="CITY")
    st = models.CharField(max_length=2, db_column="ST")
    zip = models.CharField(max_length=10, db_column="ZIP")
    county = models.CharField(max_length=100, db_column="COUNTY")
    phonenumber = models.CharField(max_length=20, db_column="PHONENUMBER")
    capmo = models.CharField(max_length=20, db_column="CAPMO", db_index=True)
    pcpname = models.CharField(max_length=255, db_column="PCPNAME")
    stat = models.CharField(max_length=50, db_column="STAT", null=True, blank=True)

    class Meta:
        db_table = 'caphistoric_report_to_use_1year'
        managed = False
        indexes = [
            models.Index(fields=['capmo']),
            models.Index(fields=['dob']),
            models.Index(fields=['plan']),
            models.Index(fields=['center']),
            models.Index(fields=['stat']),
        ]

    def __str__(self):
        return f"{self.center} - {self.plan} - {self.capmo} - {self.stat}"