from django.contrib import admin

from main.models import IngredNDB
from main.models import IngredNutr
from main.models import Recipe
from main.models import Quantity
from main.models import Rating
from main.models import RatingStat


class QuantityInline(admin.TabularInline):
    model = Quantity
    extra = 1


class IngredNutrAdmin(admin.ModelAdmin):
    inlines = (QuantityInline,)


class RecipeAdmin(admin.ModelAdmin):
    inlines = (QuantityInline,)


admin.site.register(IngredNDB)
admin.site.register(IngredNutr, IngredNutrAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Quantity)
admin.site.register(Rating)
admin.site.register(RatingStat)
