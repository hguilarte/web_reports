from django.db import models

class Membership(models.Model):
    """
    ✅ Model representing membership data.
    This model is mapped to the existing database table ('membership') and is not managed by Django.
    """
    center = models.CharField(max_length=100, db_column="CENTER", db_index=True)
    plan = models.CharField(max_length=100, db_column="PLAN", db_index=True)
    lob = models.CharField(max_length=50, db_column="LOB")
    member_id = models.CharField(max_length=50, primary_key=True, db_column="MEMBER_ID")
    medicare_id = models.CharField(max_length=50, db_column="MEDICARE_ID")
    medicaid_id = models.CharField(max_length=50, db_column="MEDICAID_ID")
    member_name = models.CharField(max_length=200, db_column="MEMBER_NAME")
    dob = models.DateField(db_column="DOB", db_index=True)
    age = models.IntegerField(db_column="AGE")
    sex = models.CharField(max_length=1, db_column="SEX")
    address = models.CharField(max_length=255, db_column="ADDRESS")
    city = models.CharField(max_length=100, db_column="CITY")
    st = models.CharField(max_length=2, db_column="ST")
    zip = models.CharField(max_length=10, db_column="ZIP")
    county = models.CharField(max_length=100, db_column="COUNTY")
    phonenumber = models.CharField(max_length=20, db_column="PHONENUMBER")
    mos = models.CharField(max_length=20, db_column="MOS", db_index=True)  # Equivalente a capmo
    mshp = models.IntegerField(db_column="MSHP")  # Equivalente a mbshp
    pcpname = models.CharField(max_length=255, db_column="PCPNAME")
    age_group = models.CharField(max_length=50, db_column="AGE_GROUP")
    stat = models.CharField(max_length=50, db_column="STAT", null=True, blank=True)

    class Meta:
        db_table = 'membership'  # ✅ Ensure the correct table mapping
        managed = False  # ✅ Prevent Django from modifying this table
        indexes = [
            models.Index(fields=['mos']),
            models.Index(fields=['dob']),
            models.Index(fields=['plan']),
            models.Index(fields=['center']),
            models.Index(fields=['stat']),
        ]

    def __str__(self):
        """
        ✅ String representation of the model instance.
        """
        return f"{self.center} - {self.plan} - {self.mos} - {self.mshp}"


class ProviderLineal(models.Model):
    """
    ✅ Model representing provider financial data.
    This model is mapped to the existing database table ('providerlineal') and is not managed by Django.
    """
    mos = models.CharField(max_length=20, db_column="MOS", db_index=True)
    medicare_id = models.CharField(max_length=50, db_column="MedicareId")
    member_full_name = models.CharField(max_length=200, db_column="MemberFullName")
    provider_fund_balance = models.DecimalField(max_digits=10, decimal_places=2, db_column="ProviderFundBalance")

    class Meta:
        db_table = 'providerlineal'  # ✅ Ensure the correct table mapping
        managed = False  # ✅ Prevent Django from modifying this table
        indexes = [
            models.Index(fields=['mos']),
            models.Index(fields=['medicare_id']),
            models.Index(fields=['member_full_name']),
        ]

    def __str__(self):
        """
        ✅ String representation of the model instance.
        """
        return f"{self.member_full_name} - {self.mos} - ${self.provider_fund_balance}"




class ClaimLineal(models.Model):
    """
    Model representing claim line details.
    """
    MOS = models.CharField(max_length=20, db_index=True)
    ClaimId = models.CharField(max_length=100, null=True, blank=True)
    ClaimLine = models.CharField(max_length=100, null=True, blank=True)
    MedicareId = models.CharField(max_length=50, db_index=True)
    MemFullName = models.CharField(max_length=200, null=True, blank=True)
    POS = models.CharField(max_length=50, null=True, blank=True)
    ClaimStartDate = models.DateField(null=True, blank=True)
    ClaimEndDate = models.DateField(null=True, blank=True)
    PaidDate = models.DateField(null=True, blank=True)
    ClaimDetailStatus = models.CharField(max_length=50, null=True, blank=True)
    AmountPaid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    AdminFee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ProvFullName = models.CharField(max_length=200, null=True, blank=True)
    ProvSpecialty = models.CharField(max_length=200, null=True, blank=True)
    MemDOB = models.DateField(null=True, blank=True)
    MemAge = models.IntegerField(null=True, blank=True)
    MemPCPFullName = models.CharField(max_length=200, null=True, blank=True)
    CarrierMemberID = models.CharField(max_length=100, null=True, blank=True)
    MemEnrollId = models.CharField(max_length=100, null=True, blank=True)
    Diagnoses = models.TextField(null=True, blank=True)
    AllowAmt = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    PharmacyName = models.CharField(max_length=200, null=True, blank=True)
    NPOS = models.CharField(max_length=50, null=True, blank=True)
    Pharmacy = models.CharField(max_length=200, null=True, blank=True)
    Claims = models.IntegerField(null=True, blank=True)
    County_Simple = models.CharField(max_length=100, db_column="County Simple", null=True, blank=True)
    NPOS_Simple = models.CharField(max_length=100, db_column="NPOS Simple", null=True, blank=True)
    Triangle_Cover = models.CharField(max_length=100, db_column="Triangle Cover", null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'claimlineal'
        indexes = [
            models.Index(fields=['MOS']),
            models.Index(fields=['MedicareId']),
        ]
        # ❌ NO usar default_auto_field ni primary_key si no hay clave
        # ❌ NO declarar unique_together si no aplica

    def __str__(self):
        return f"{self.MedicareId} - {self.MOS}"