from django.db import models

from django.utils import timezone
from django.utils.http import urlquote
from django.core.mail import send_mail

from django.contrib.auth.models import User


# ---- Ingredient Model ---------------------------------------------
class IngredNDB(models.Model):

    # Ingredient USDA Nutrition Database (NDB) number and description
    ndb_no = models.CharField(max_length=255, null=False, blank=False)
    ndb_description = models.CharField(max_length=255, null=False, blank=False)
    flag = models.BooleanField(blank=True)

    def __unicode__(self):
        return self.ndb_description


class IngredNutr(models.Model):
    ndb_id = models.ForeignKey(IngredNDB)
    handle = models.CharField(max_length=255, null=False, blank=True)

    eqv = models.DecimalField(default=0, max_digits=7, decimal_places=3, null=False, blank=True)
    qty = models.DecimalField(default=1, max_digits=7, decimal_places=3, null=False, blank=True)
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

    def __unicode__(self):
        return self.handle


# ---- Recipe Model -------------------------------------------------
class Recipe(models.Model):
    ingred = models.ManyToManyField(IngredNutr, through='main.Quantity')

    name = models.CharField(max_length=255, null=False, blank=True)
    description = models.TextField(null=False, blank=True)
    category = models.CharField(max_length=255)
    tags = models.TextField(null=False, blank=True)
    servings_orig = models.DecimalField(default=1, max_digits=7, decimal_places=2, null=False, blank=True)
    servings_scaled = models.DecimalField(default=1, max_digits=7, decimal_places=2, null=False, blank=True)

    calories_tot = models.IntegerField(default=0, null=False, blank=True)
    time_prep = models.TimeField(auto_now=False, auto_now_add=False, default="0:00")
    time_cook = models.TimeField(auto_now=False, auto_now_add=False, default="0:00")
    time_tot = models.TimeField(auto_now=False, auto_now_add=False, default="0:00")

    directions = models.TextField(null=False, blank=True)
    author = models.CharField(max_length=255, null=True, blank=True)
    owner = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='recipe_img', null=True, blank=True)

    def __unicode__(self):
        return self.name


# ---- Quantity Model ---------------------------------------------
class Quantity(models.Model):
    handle = models.CharField(max_length=255, null=False, blank=True)
    ingred = models.ForeignKey(IngredNutr)
    recipe = models.ForeignKey(Recipe)

    name_common = models.CharField(max_length=255, null=False, blank=True)

    # The amount of the ingred, in the units specified in IngredNutr
    qty_common = models.CharField(max_length=5, null=False, blank=True)
    qty_prop = models.DecimalField(default=1, max_digits=7, decimal_places=3, null=False, blank=True)
    qty_scaled = models.DecimalField(default=1, max_digits=7, decimal_places=3, null=False, blank=True)

    def __unicode__(self):
        return self.handle


# ---- Comment Model ------------------------------------------------
class Comment(models.Model):
    handle = models.CharField(max_length=255, null=False, blank=True)
    recipe = models.ForeignKey(Recipe)
    text = models.TextField(blank=False)
    time_stamp = models.DateTimeField(auto_now_add=True)
    user_name = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(blank=False)
    web_page = models.URLField(blank=True)
    number = models.IntegerField(default=200, null=False, blank=True)

    def __unicode__(self):
        return self.handle


# ---- Vote Model ---------------------------------------------------
class Vote(models.Model):
    handle = models.CharField(max_length=200, null=False, blank=False)
    recipe = models.ForeignKey(Recipe)
    user = models.ManyToManyField(User)
    state = models.IntegerField(default=0, null=False, blank=True)

    def __unicode__(self):
        return self.handle


# ---- VoteStat Model ----------------------------------------------
class VoteStat(models.Model):
    recipe = models.OneToOneField(Recipe)
    v_up = models.IntegerField(default=0, null=False, blank=True)
    v_dn = models.IntegerField(default=0, null=False, blank=True)
    v_tot = models.IntegerField(default=0, null=False, blank=True)

    v_up_p = models.DecimalField(default=0, max_digits=4, decimal_places=1, null=False, blank=True)
    v_dn_p = models.DecimalField(default=0, max_digits=4, decimal_places=1, null=False, blank=True)

    def __unicode__(self):
        return unicode(self.id)
