from django.contrib import admin

from main.models import IngredNDB
from main.models import IngredNutr
from main.models import Recipe
from main.models import Quantity

admin.site.register(IngredNDB)
admin.site.register(IngredNutr)
admin.site.register(Recipe)
admin.site.register(Quantity)
