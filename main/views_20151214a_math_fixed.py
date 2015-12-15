import json
import requests
import re

from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import RequestContext

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse

from main.forms import RecipeAddForm, RecipeEditForm
from main.forms import IngredAddForm
from main.forms import UserSignUp, UserSignIn
from main.forms import CommentForm

from main.models import IngredNDB, IngredNutr, Recipe, Quantity
from main.models import Comment, Vote, VoteStat, Rating, RatingStat


# ---- About View ---------------------------------------------------
def about_view(request):
    context = {}

    return render_to_response('about.html', context,
                              context_instance=RequestContext(request))


# ---- IngredNDB List -----------------------------------------------
def IngredNDBListView(request):

    context = {}

    ingredndb = IngredNDB.objects.all()
    context['ingreds'] = ingredndb

    return render_to_response('ingred_ndb_list.html', context,
                              context_instance=RequestContext(request))


# ---- Query NDB API ------------------------------------------------
def NDBQuery(ndb_no):
    base = 'http://api.nal.usda.gov/ndb/reports/'
    param_dict = {
                  'ndbno': ndb_no,
                  'type': 'b',
                  'format': 'json',
                  'api_key': 'ZTghPLc6kCs7l1cOqBpgMIS3QcAtru7x7GvAAh80',
                  }

    response = requests.get(base, params=param_dict)

    nutr_list = response.json().get('report').get('food').get('nutrients')

    return nutr_list


# ---- Get Standard Nutrition info ----------------------------------
def GetNutrInfo(nutr_list):
    """nutrient_id_list: The nutrients I have chosen to show with recipes.
    Water: 255; Energy (kcal): 208; Protein: 203; Total Lipid (fat): 204;
    Carbohydrate, by difference: 205; Fiber, total dietary: 291;
    Sugars, total: 269; Sodium: 307. They are listed in the order they
    appear in the json. The energy from protein, carbohydrates, and fat
    are calculated with a 4:4:9 proportion. Since protein and carbohydrates
    have the same value, I am using energy_ptn to represent both. The
    id numbers for the calculated energies are my own; the do not come from
    NDB. nutrient_id_list = [255, 208, 203, 204, 205, 291, 269, 307] """

    #  Initialize the variables
    full_nutr_info = []
    basic_nutr_info = {255: ['water', 0],
                       208: ['energy_tot', 0],
                       203: ['protein', 0],
                       204: ['lipids', 0],
                       205: ['carbs', 0],
                       291: ['fiber', 0],
                       269: ['sugars', 0],
                       307: ['sodium', 0],
                       997: ['energy_cho', 0],
                       998: ['energy_ptn', 0],
                       999: ['energy_fat', 0],
                       }

    # Get the nutritional info for the ingredient
    for nutr in nutr_list:
        full_nutr_info.append([nutr['name'], nutr['value'], nutr['unit']])

        nutr_id = int(nutr['nutrient_id'])

        if nutr_id in basic_nutr_info:
            basic_nutr_info[nutr_id][1] = float(nutr['value'])

    # Calculate energy contributions from Protein, Lipids, Carbs
    energy_tot = basic_nutr_info[208][1]

    protein_en = 4 * basic_nutr_info[203][1]
    fat_en = 9 * basic_nutr_info[204][1]
    carbs_en = 4 * basic_nutr_info[205][1]

    energy_calc = protein_en + fat_en + carbs_en
    ratio = energy_tot / energy_calc

    basic_nutr_info[997][1] = carbs_en * ratio
    basic_nutr_info[998][1] = protein_en * ratio
    basic_nutr_info[999][1] = fat_en * ratio

    return [basic_nutr_info, full_nutr_info]


# ---- Make a list of Forms/Units -----------------------------------
def GetMeasures(measures):

    measures_list = []

    for mea in measures:
        eqv = mea['eqv']
        qty = mea['qty']
        label = mea['label']

        measures_list.append([eqv, qty, label])

    return measures_list


def MakeNewIngredNutr(ingred, measures, basic_nutr_info):
    for mea in measures:

        eqv = mea['eqv']
        qty = mea['qty']
        label = mea['label']

        num = ingred.ndb_no
        desc = ingred.ndb_description
        handle = ' '.join([num, desc, str(qty), label])

        prop = eqv / 100

        ingred_nutr, created = IngredNutr.objects.get_or_create(handle=handle,
                                                                ndb_id=ingred)

        ingred_nutr.ndb_num = num

        ingred_nutr.eqv = eqv
        ingred_nutr.qty = qty
        ingred_nutr.label = label

        ingred_nutr.water = basic_nutr_info[255][1] * prop
        ingred_nutr.protein = basic_nutr_info[203][1] * prop
        ingred_nutr.lipids = basic_nutr_info[204][1] * prop
        ingred_nutr.carbs = basic_nutr_info[205][1] * prop
        ingred_nutr.fiber = basic_nutr_info[291][1] * prop
        ingred_nutr.sugars = basic_nutr_info[269][1] * prop
        ingred_nutr.sodium = basic_nutr_info[307][1] * prop

        ingred_nutr.energy_tot = basic_nutr_info[208][1] * prop
        ingred_nutr.energy_cho = basic_nutr_info[997][1] * prop
        ingred_nutr.energy_ptn = basic_nutr_info[998][1] * prop
        ingred_nutr.energy_fat = basic_nutr_info[999][1] * prop

        ingred_nutr.save()

    return created


# ---- IngredNDB Detail ---------------------------------------------
def IngredNDBDetailView(request, pk):

    context = {}

    ingred = IngredNDB.objects.get(pk=pk)
    context['ingred_v'] = ingred

    # Retrieve list of nutrients from NDB API
    nutr_list = NDBQuery(ingred.ndb_no)
    measures = nutr_list[0]['measures']

    # Extract Basic [0] and Full [1] Nutrition Info from nutr_list
    nutr_info = GetNutrInfo(nutr_list)

    context['nutr_list'] = nutr_info[1]
    context['measures'] = GetMeasures(measures)

    # Get or Create new IngredNutr(s) (ie, I have not pre-populated the
    # IngredNutr database; as the user looks at ingredients they get saved
    # in the database and subsequent views come from the db and not API.)
    MakeNewIngredNutr(ingred, measures, nutr_info[0])

    return render_to_response('ingred_ndb_detail.html', context,
                              context_instance=RequestContext(request))


#  ---- Adding Ingredients to a Recipe ------------------------------
# Currently does not remove duplicates from output
def get_ingred_ndb_json(request):
    search_text = request.GET.get('search', '')
    object_list = []

    rgx = re.compile("(\w[\w']*\w|\w)")
    search_list = rgx.findall(search_text)

    for search in search_list:
        objects = IngredNDB.objects.filter(
            ndb_description__icontains=search
        )
        for obj in objects:
            object_list.append([obj.ndb_no, obj.ndb_description])

    return JsonResponse(object_list, safe=False)


def JsonIngredNutr(request):
    ndb_no = request.GET.get('search2', '')

    nutr_list = NDBQuery(ndb_no)

    ingred = IngredNDB.objects.get(ndb_no=ndb_no)
    measures = nutr_list[0]['measures']
    nutr_info = GetNutrInfo(nutr_list)
    MakeNewIngredNutr(ingred, measures, nutr_info[0])

    objects = IngredNutr.objects.filter(
        handle__icontains=ndb_no
        )

    object_list = []
    for obj in objects:
        object_list.append([obj.qty, obj.label])

    return JsonResponse(object_list, safe=False)


def recipe_attr_edit_func(request, pk):

    attr = request.GET.get('attr', '')
    new_value = request.GET.get('new_value', '')
    recipe = Recipe.objects.get(pk=pk)

    setattr(recipe, attr, new_value)

    recipe.save()

    return HttpResponse(status=200)


def add_quantity(request, pk):

    name_common = request.GET.get('name_common', '')
    ndb_num = request.GET.get('ndb_num', '')
    ndb_desc = request.GET.get('ndb_desc', '')
    ndb_quant = request.GET.get('ndb_quant', '')
    form_or_unit = request.GET.get('form_or_unit', '')
    qty_common_str = str(request.GET.get('qty_common', ''))

    quant_handle = ' '.join([ndb_num, pk, name_common])

    recipe = Recipe.objects.get(pk=pk)
    ingred_ndb = IngredNDB.objects.get(ndb_no=ndb_num)
    ingred_nutr = IngredNutr.objects.filter(
        handle__icontains=ndb_num).filter(
        handle__icontains=form_or_unit).filter(
        handle__icontains=ndb_quant[0:2])[0]

    quant_obj, created = Quantity.objects.get_or_create(
        recipe=recipe,
        ingred=ingred_nutr,
        handle=quant_handle
        )

    quant_obj.qty_common = qty_common_str
    quant_obj.name_common = name_common

    qty_prop = round(float(qty_common_str) / float(ingred_nutr.qty), 3)
    quant_obj.qty_prop = qty_prop

    quant_obj.save()

    return HttpResponse(status=200)


# ---- Recipe List --------------------------------------------------
def RecipeListView(request):
    context = {}
    recipes = Recipe.objects.all()
    context['recipes'] = recipes

    return render_to_response('recipe_list.html', context,
                              context_instance=RequestContext(request))


# ---- Tabulate Basic Nutrition Info for Recipe ---------------------
def tabulate_basic_nutr(recipe):
    nutr_basic_g = {'water': 0,
                    'protein': 0,
                    'lipids': 0,
                    'carbs': 0,
                    'fiber': 0,
                    'sugars': 0,
                    }

    nutr_other_mg = {'sodium': 0}

    energy_basic = {'energy_tot': 0,
                    'energy_cho': 0,
                    'energy_ptn': 0,
                    'energy_fat': 0,
                    }

    nutr_individ = {}

    servings = recipe.servings_orig
    # Retrieve and sum nutrition values for each nutrient in each ingredient
    for quant in recipe.quantity_set.all():

        qty_prop = quant.qty_prop
        ingred_obj = quant.ingred

        ingred_num = quant.ingred.ndb_num
        nutr_individ[ingred_num] = {'nutr_basic_g': {},
                                    'nutr_other_mg': {},
                                    'energy_basic': {},
                                    'mass': 0
                                    }

        for nutr in nutr_basic_g:
            nutr_value = getattr(ingred_obj, nutr)
            value_scaled = nutr_value * qty_prop

            nutr_basic_g[nutr] += value_scaled
            nutr_individ[ingred_num]['nutr_basic_g'][nutr] = value_scaled

        for nutr in nutr_other_mg:
            nutr_value = getattr(ingred_obj, nutr)
            value_scaled = nutr_value * qty_prop

            nutr_other_mg[nutr] += value_scaled
            nutr_individ[ingred_num]['nutr_other_mg'][nutr] = value_scaled

        for energy in energy_basic:
            energy_value = getattr(ingred_obj, energy)
            value_scaled = energy_value * qty_prop

            energy_basic[energy] += value_scaled
            nutr_individ[ingred_num]['energy_basic'][energy] = value_scaled

    return [nutr_basic_g, nutr_other_mg, energy_basic, servings, nutr_individ]


# ---- Scale Nutrition Info per serving; deal with decimals ---------
def scale_basic_nutr(nutr_basic_g, nutr_other_mg, energy_basic, servings, nutr_individ):
    mass_basic = 0
    for nutr in nutr_basic_g:
        mass = nutr_basic_g[nutr] / servings
        nutr_basic_g[nutr] = int(round(mass, 0))
        mass_basic += mass

    for nutr in nutr_other_mg:
        mass = nutr_other_mg[nutr] / servings
        nutr_other_mg[nutr] = int(round(mass, 0))
        mass_basic += mass / 1000

    for energy in energy_basic:
        energy_basic[energy] = int(round(energy_basic[energy] / servings, 0))

    mass_basic = int(round(mass_basic, 0))

    for nutr in nutr_individ:
        mass_individ = 0
        for bas in nutr_individ[nutr]['nutr_basic_g']:
            mass = nutr_individ[nutr]['nutr_basic_g'][bas] / servings
            nutr_individ[nutr]['nutr_basic_g'][bas] = int(round(mass, 0))
            mass_individ += mass

        for other in nutr_individ[nutr]['nutr_other_mg']:
            mass = nutr_individ[nutr]['nutr_other_mg'][other] / servings
            nutr_individ[nutr]['nutr_other_mg'][other] = int(round(mass, 0))
            mass_individ += mass / 1000

        for bas in nutr_individ[nutr]['energy_basic']:
            mass = nutr_individ[nutr]['energy_basic'][bas] / servings
            nutr_individ[nutr]['energy_basic'][bas] = int(round(mass, 0))

        nutr_individ[nutr]['mass'] = int(round(mass_individ, 0))

    return [nutr_basic_g, nutr_other_mg,
            energy_basic, mass_basic, nutr_individ]


# ---- Get Rating and Rating Stats ----------------------------------
def get_ratings(active, request, pk, recipe):
    if active:
        h_temp = "_".join([str(pk), str(request.user.username)])
        rating, created = Rating.objects.get_or_create(recipe=recipe,
                                                       handle=h_temp)
        if created:
            return HttpResponseRedirect('/rating_stats_func/%s' % pk)
        rating_v = rating
    else:
        rating_v = -1

    return rating_v


# ---- Get Rating stats ---------------------------------------------
def get_rating_stats(recipe):
    rating_stat, created = RatingStat.objects.get_or_create(recipe=recipe)

    return rating_stat


# ---- Get Old Comments ---------------------------------------------
def get_old_comments(recipe):

    return Comment.objects.filter(recipe=recipe)


# ---- Get New Comments ---------------------------------------------
def get_new_comments(from_form, request, old_comments, pk):
    new_comment = from_form.save()

    user_name = request.user.username
    time = str(new_comment.time_stamp)

    # Number comments so deletions by moderator don't change other #s
    length = len(old_comments)
    print "length: %s" % length
    if length == 1:
        number = length
    else:
        number = old_comments[length - 2].number + 1
        print "number: %s" % number

    new_comment.user_name = user_name
    new_comment.handle = "_".join([str(pk), user_name, time])
    new_comment.number = number
    new_comment.email = request.user.email
    new_comment.save()

    return "Success"


# ---- Recipe Detail ------------------------------------------------
def recipe_detail(request, pk):

    context = {}
    recipe = Recipe.objects.get(pk=pk)

    # Tabulate basic nutrition info
    tab = tabulate_basic_nutr(recipe)

    # Account for servings per recipe; round numbers; calc total mass
    sca = scale_basic_nutr(tab[0], tab[1], tab[2], tab[3], tab[4])

    # Save the total number of calories per serving to the database
    recipe.calories_tot = sca[2]['energy_tot']
    recipe.save()

    # Authenticate the user
    active = request.user.is_authenticated()

    # # Handle Comments
    old_comments = get_old_comments(recipe)
    if active:
        cntxt_comments_v = CommentForm(initial={'recipe': pk})
        if request.method == 'POST':
            from_form = CommentForm(request.POST)
            if from_form.is_valid():
                get_new_comments(from_form, request, old_comments, pk)
                return HttpResponseRedirect('/recipe_detail/%s/' % pk)

    # Context Variables
    context['recipe'] = recipe

    context['nutr_basic'] = sca[0]
    context['nutr_other'] = sca[1]
    context['energy_basic'] = sca[2]
    context['mass_basic'] = sca[3]

    context['nutr_individ'] = json.dumps(sca[4])

    # print  "%s" % json.dumps(sca[4])
    context['text_dict'] = json.dumps(sca[4])

    context['active'] = active

    context['rating_v'] = get_ratings(active, request, pk, recipe)
    context['rating_stat_v'] = get_rating_stats(recipe)

    context['old_comments_v'] = old_comments
    context['comments_v'] = cntxt_comments_v

    # Send data to template -----------------------------------------
    return render_to_response('recipe_detail.html', context,
                              context_instance=RequestContext(request))


# ---- Add, Edit, and Delete Recipes (models.py Recipe) -------------
def recipe_create_func(request):

    owner = str(request.user.username)
    recipe = Recipe.objects.create(
        owner=owner,
        name="New Recipe",
        servings_orig=1,
        image="/static/img/food_default_300px.jpg")
    url = reverse('recipe_detail', args=([recipe.id]))

    return HttpResponseRedirect(url)


def recipe_edit(request, pk):

    context = {}

    recipe = Recipe.objects.get(pk=pk)
    form = RecipeEditForm(request.POST or None, instance=recipe)

    context['recipe_e'] = recipe
    context['form_recipe_edit'] = form

    if form.is_valid():
        form.save()
        return HttpResponseRedirect('/recipe_detail/%s' % pk)
    else:
        print form.errors

    return render_to_response('recipe_edit.html', context,
                              context_instance=RequestContext(request))


def activate_edit_flag(request, pk):
    recipe = Recipe.objects.get(pk=pk)
    recipe.edit_flag = True
    recipe.save()

    return HttpResponse(status=200)


def recipe_delete_func(request, pk):

    Recipe.objects.get(pk=pk).delete()

    return HttpResponseRedirect('/recipe_list/')


def recipe_delete_page(request, pk):

    context = {}

    context['recipe_del'] = Recipe.objects.get(pk=pk)

    return render_to_response('recipe_delete_page.html', context,
                              context_instance=RequestContext(request))


# ---- Add and Delete Ingredients (models.py Ingredient) ------------
def ingred_add(request):

    context = {}

    form = IngredAddForm()
    context['form_ingred_add'] = form

    if request.method == 'POST':
        form = IngredAddForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/ingred_list/')
        else:
            context['errors'] = form.errors

    return render_to_response('ingred_add.html', context,
                              context_instance=RequestContext(request))


def ingred_del_func(request, pk):

    IngredNutr.objects.get(pk=pk).delete()

    return HttpResponseRedirect('/ingred_list/')


def ingred_del_page(request, pk):

    context = {}

    context['ingred_del'] = IngredNutr.objects.get(pk=pk)

    return render_to_response('ingred_del_page.html', context,
                              context_instance=RequestContext(request))


# ---- Sign Users Up ------------------------------------------------
def sign_up(request):
    context = {}

    form = UserSignUp()
    context['form'] = form

    if request.method == 'POST':
        form = UserSignUp(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            user_name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                new_user = User.objects.create_user(user_name,
                                                    email,
                                                    password
                                                    )
                new_user.first_name = first_name
                new_user.last_name = last_name
                new_user.save()

                auth_user = authenticate(username=user_name,
                                         password=password)

                if auth_user is not None:
                    context['valid'] = "Thank you for signing up!"

                    login(request, auth_user)

                    return HttpResponseRedirect('/')

                else:
                    context['valid'] = "User sign-up failed. Please try again."

            except IntegrityError, e:
                context['valid'] = "A User with that name already exists."

        else:
            context['valid'] = form.errors

    if request.method == 'GET':
        context['valid'] = "Please Sign Up!"

    return render_to_response('sign_up.html', context,
                              context_instance=RequestContext(request))


# ---- Sign Users In ------------------------------------------------
def sign_in(request):
    context = {}

    context['form'] = UserSignIn()

    if request.method == 'POST':
        form = UserSignIn(request.POST)

        if form.is_valid():
            user_name = form.cleaned_data['name']
            password = form.cleaned_data['password']

            auth_user = authenticate(username=user_name,
                                     password=password
                                     )
            print "authenticate passed"
            print auth_user

            if auth_user is not None:
                print "auth_user not None"
                if auth_user.is_active:
                    login(request, auth_user)
                    context['valid'] = "Sign In Successful"

                return HttpResponseRedirect('/')

            else:
                context['valid'] = "Sign In Failed: Invalid User"
                print "auth_user is apparently None"

        context['valid'] = "Please enter a User name"

    if request.method == 'GET':
        context['valid'] = "Please Sign In!"

    return render_to_response('sign_in.html', context,
                              context_instance=RequestContext(request))


# ---- Sign Users Out -----------------------------------------------
def sign_out(request):

    logout(request)

    return HttpResponseRedirect('/sign_in/')


# ---- Delete Users -------------------------------------------------
def user_del_func(request):

    username_in = User.username
    User.objects.get(username=username_in).delete()

    return HttpResponseRedirect('/')


def user_del_page(request):

    context = {}

    print User.is_active
    print request.user.username
    print request.user.first_name

    # context['user_del'] = User.objects.get(username=username_in)

    return render_to_response('user_del_page.html', context,
                              context_instance=RequestContext(request))


# ---- Rating Recipes -----------------------------------------------
def rating_func(request, pk):

    rating_new = request.GET.get('rating_new', '')

    h_temp = "_".join([str(pk), str(request.user)])
    rating_cur = Rating.objects.get(handle=h_temp)

    rating_cur.rating = rating_new

    rating_cur.save()

    # return HttpResponse(status=200)
    return HttpResponseRedirect('/rating_stats_func/%s' % pk)


def rating_stats_func(request, pk):

    # Count (zero and non-zero) ratings for the given Recipe --------
    r0_obj = Rating.objects.filter(recipe=pk)
    r0_len = len(r0_obj)

    r_obj = r0_obj.exclude(rating=0)
    r_count = len(r_obj)
    r0_count = r0_len - r_count

    # Sum ratings and collect data for distribution / histogram -----
    r_sum = 0
    r_distrib = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for r in r_obj:
        r_sum += r.rating
        r_distrib[int(r.rating)] += 1

    # Find the average rating for the given Recipe ------------------
    if r_count == 0:
        r_avg = 0
    else:
        r_avg = float(r_sum) / float(r_count)

    # Calculate histogram % for each star-rating --------------------
    r_percent = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    if r_count > 0:
        for r in r_percent:
            r_percent[r] = r_distrib[r] * 100 / r_count
    else:
        pass

    # Save stats to RatingStat model --------------------------------
    rating_stat, created = RatingStat.objects.get_or_create(recipe_id=pk)

    rating_stat.count = r_count
    rating_stat.avg = r_avg

    # Populate distrib and % fields: (r0_d; r1_d, r2_d, ...; r1_p, r2_p, ...)
    rating_stat.r0_d = r0_count
    for r in r_distrib:
        attr_distrib = "r%s_d" % r
        val_distrib = r_distrib[r]
        setattr(rating_stat, attr_distrib, val_distrib)

        attr_percent = "r%s_p" % r
        val_percent = r_percent[r]
        setattr(rating_stat, attr_percent, val_percent)

    rating_stat.save()

    return HttpResponseRedirect('/recipe_detail/%s' % pk)
