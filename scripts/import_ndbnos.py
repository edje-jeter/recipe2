#!/usr/bin/env python

import csv
import sys
import os

sys.path.append('..')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

from main.models import IngredNDB

dir_name = os.path.dirname(os.path.abspath(__file__))
print dir_name
file_name = "NDB_28_food_list_20151102.csv"

ndbno_csv = os.path.join(dir_name, file_name)
print ndbno_csv

csv_file = open(ndbno_csv, 'r')

reader = csv.DictReader(csv_file)

for row in reader:
    new_ingredndb, created = IngredNDB.objects.get_or_create(ndb_no=row['NDB_NO'])
    new_ingredndb.ndb_description = row['Description']
    new_ingredndb.save()
    print new_ingredndb.ndb_description
