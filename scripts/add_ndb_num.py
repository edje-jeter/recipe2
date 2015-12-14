#!/usr/bin/env python

import csv
import sys
import os

sys.path.append('..')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

from main.models import IngredNDB, IngredNutr

i = 1
for i in range(1, 200):
    try:
        ingred = IngredNutr.objects.get(pk=i)
    except Exception, e:
        pass

    ingred.ndb_num = ingred.handle[0:5]
    ingred.save()
    print ingred.handle[0:5]
