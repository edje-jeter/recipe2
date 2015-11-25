import requests

from django.shortcuts import render, render_to_response
from django.template import RequestContext

from main.models import IngredNDB, IngredNutr


# ---- IngredNDB List -----------------------------------------------
def IngredNDBListView(request):

    context = {}

    ingredndb = IngredNDB.objects.all()
    context['ingreds'] = ingredndb

    return render_to_response('ingred_ndb_list.html', context,
                              context_instance=RequestContext(request))


def IngredNDBDetailView(request, pk):

    context = {}

    ingred = IngredNDB.objects.get(pk=pk)
    context['ingred_v'] = ingred

    # Access-information for Nutrient Database (NDB) API ------------
    base = 'http://api.nal.usda.gov/ndb/reports/'
    param_dict = {
                  'ndbno': ingred.ndb_no,
                  'type': 'b',
                  'format': 'json',
                  'api_key': 'ZTghPLc6kCs7l1cOqBpgMIS3QcAtru7x7GvAAh80',
                  }

    response = requests.get(base, params=param_dict)

    nutr_list = response.json().get('report').get('food').get('nutrients')

    # ---- Populate full nutrition info -----------------------------
    a = []
    for nutr in nutr_list:
        a.append([nutr['name'], nutr['value'], nutr['unit']])

    context['nutr_list'] = a

    # nutrient_id_list: The nutrients I have chosen to show with recipes.
    # Water: 255; Energy (kcal): 208; Protein: 203; Total Lipid (fat): 204;
    # Carbohydrate, by difference: 205; Fiber, total dietary: 291;
    # Sugars, total: 269; Sodium: 307. It's inside the for loop so that it
    # resets each time we go through the loop
    nutrient_id_list = [255, 208, 203, 204, 205, 291, 269, 307]

    water = 0
    protein = 0
    lipids = 0
    carbs = 0
    fiber = 0
    sugars = 0
    sodium = 0
    energy_tot = 0
    energy_ptn = 0
    energy_cho = 0
    energy_fat = 0

    # Get the basic nutritional info for the ingredient
    for nutr in nutr_list:

        nutr_id = int(nutr['nutrient_id'])
        print "nutr_id: %s" % nutr_id

        print "nutr_id_list: %s" % nutrient_id_list
        if nutrient_id_list == []:
            break

        if nutr_id in nutrient_id_list:
            print "checkpoint 1"
            if nutr_id == 255:
                water = float(nutr['value'])
                nutrient_id_list.remove(nutr_id)
                print "water: %s" % water

            elif nutr_id == 203:
                protein = float(nutr['value'])
                nutrient_id_list.remove(nutr_id)

            elif nutr_id == 204:
                lipids = float(nutr['value'])
                nutrient_id_list.remove(nutr_id)

            elif nutr_id == 205:
                carbs = float(nutr['value'])
                nutrient_id_list.remove(nutr_id)
                print "carbs: %s" % carbs

            elif nutr_id == 291:
                fiber = float(nutr['value'])
                nutrient_id_list.remove(nutr_id)

            elif nutr_id == 269:
                sugars = float(nutr['value'])
                nutrient_id_list.remove(nutr_id)
                print "sugars: %s" % sugars

            elif nutr_id == 307:
                sodium = float(nutr['value'])
                nutrient_id_list.remove(nutr_id)

            elif nutr_id == 208:
                en_tot = int(nutr['value'])
                energy_tot = en_tot

                energy_ptn = en_tot * 4 / 17
                energy_cho = energy_ptn
                energy_fat = en_tot * 9 / 17

                nutrient_id_list.remove(nutr_id)

        else:
            pass

    # ---- Populate measurement info --------------------------------
    b = []
    measures = nutr_list[0]['measures']
    for mea in measures:
        eqv = mea['eqv']
        qty = mea['qty']
        label = mea['label']
        num = ingred.ndb_no
        desc = ingred.ndb_description
        handle = ' '.join([num, desc, str(qty), label])
        # print handle

        prop = eqv / 100
        print prop

        ingred_nutr, created = IngredNutr.objects.get_or_create(handle=handle,
                                                                ndb_id=ingred)

        ingred_nutr.eqv = eqv
        ingred_nutr.qty = qty
        ingred_nutr.label = label

        ingred_nutr.water = water * prop
        ingred_nutr.protein = protein * prop
        ingred_nutr.lipids = lipids * prop
        ingred_nutr.carbs = carbs * prop
        ingred_nutr.fiber = fiber * prop
        ingred_nutr.sugars = sugars * prop
        ingred_nutr.sodium = sodium * prop

        ingred_nutr.energy_tot = energy_tot * prop
        ingred_nutr.energy_ptn = energy_ptn * prop
        ingred_nutr.energy_cho = energy_cho * prop
        ingred_nutr.energy_fat = energy_fat * prop

        ingred_nutr.save()

        b.append([mea['eqv'], qty, label])

    context['measures'] = b

    # ---- Populate basic nutrition info for each measure -----------





    # Send data to template -----------------------------------------
    return render_to_response('ingred_ndb_detail.html', context,
                              context_instance=RequestContext(request))
