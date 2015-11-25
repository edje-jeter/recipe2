from django.db import models


# ---- Ingredient Model ---------------------------------------------
class IngredNDB(models.Model):

    # Ingredient USDA Nutrition Database (NDB) number and description
    ndb_no = models.CharField(max_length=255, null=False, blank=False)
    ndb_description = models.CharField(max_length=255, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=True)

    def __unicode__(self):
        return self.ndb_description


class IngredNutr(models.Model):
    ndb_id = models.ForeignKey(IngredNDB)
    handle = models.CharField(max_length=255, null=False, blank=True)

    eqv = models.DecimalField(default=0, max_digits=7, decimal_places=3, null=False, blank=True)
    qty = models.DecimalField(default=0, max_digits=7, decimal_places=3, null=False, blank=True)
    label = models.CharField(max_length=255, null=False, blank=True)

    # Amount (in g [Sodium: mg]) of key components in 100g of Ingredient
    water = models.DecimalField(default=0, max_digits=7, decimal_places=3, null=False, blank=True)
    protein = models.DecimalField(default=0, max_digits=7, decimal_places=3, null=False, blank=True)
    lipids = models.DecimalField(default=0, max_digits=7, decimal_places=3, null=False, blank=True)
    carbs = models.DecimalField(default=0, max_digits=7, decimal_places=3, null=False, blank=True)
    fiber = models.DecimalField(default=0, max_digits=7, decimal_places=3, null=False, blank=True)
    sugars = models.DecimalField(default=0, max_digits=7, decimal_places=3, null=False, blank=True)
    sodium = models.DecimalField(default=0, max_digits=7, decimal_places=3, null=False, blank=True)

    # The energy in kcal in 100g of Ingredient, plus contributions from
    # protein, fat, and carbohydrates using 4-9-4 proportion
    energy_tot = models.DecimalField(default=0, max_digits=7, decimal_places=3, null=False, blank=True)
    energy_ptn = models.DecimalField(default=0, max_digits=7, decimal_places=3, null=False, blank=True)
    energy_fat = models.DecimalField(default=0, max_digits=7, decimal_places=3, null=False, blank=True)
    energy_cho = models.DecimalField(default=0, max_digits=7, decimal_places=3, null=False, blank=True)

    def __unicode__(self):
        return self.handle
