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
from main.models import Comment, Vote, VoteStat


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
                       998: ['energy_ptn', 0],
                       999: ['energy_fat', 0],
                       }

    # Get the nutritional info for the ingredient
    for nutr in nutr_list:
        full_nutr_info.append([nutr['name'], nutr['value'], nutr['unit']])

        nutr_id = int(nutr['nutrient_id'])

        if nutr_id in basic_nutr_info:
            basic_nutr_info[nutr_id][1] = float(nutr['value'])

    energy_tot = basic_nutr_info[208][1]

    basic_nutr_info[998][1] = energy_tot * 4 / 17
    basic_nutr_info[999][1] = energy_tot * 9 / 17

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
def JsonIngredNDB(request):
    search_string = request.GET.get('search', '')

    objects = IngredNDB.objects.filter(
        ndb_description__icontains=search_string
        )

    object_list = []
    for obj in objects:
        object_list.append([obj.ndb_no, obj.ndb_description])

    return JsonResponse(object_list, safe=False)


# Currently does not remove duplicates from output
def json_ingred_ndb_2(request):
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
    # print "ndb_no: %s" % ndb_no

    nutr_list = NDBQuery(ndb_no)
    # print "nutr_list: %s" % nutr_list

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


def RecipeUpdate(request, pk):

    context = {}
    recipe = Recipe.objects.get(pk=pk)
    context['recipe'] = recipe

    nutr_basic_g = {'water': 0,
                    'protein': 0,
                    'lipids': 0,
                    'carbs': 0,
                    'fiber': 0,
                    'sugars': 0,
                    }

    nutr_other_mg = {'sodium': 0}

    energy_basic = {'energy_tot': 0,
                    'energy_ptn': 0,
                    'energy_fat': 0,
                    }

    # Retrieve and sum nutrition values for each nutrient in each ingredient
    for quant in recipe.quantity_set.all():
        # ndb_no = ingred.ingred.ndb_id.ndb_no
        # nutr_list = NDBQuery(ndb_no)

        # print quant.qty_common
        # print quant.ingred.label
        # print quant.name_common

        qty_prop = quant.qty_prop
        servings = quant.recipe.servings_orig

        for nutr in nutr_basic_g:
            nutr_value = getattr(quant.ingred, nutr)
            nutr_basic_g[nutr] += nutr_value * qty_prop

        for nutr in nutr_other_mg:
            nutr_value = getattr(quant.ingred, nutr)
            nutr_other_mg[nutr] += nutr_value * qty_prop

        for energy in energy_basic:
            energy_value = getattr(quant.ingred, energy)
            energy_basic[energy] += energy_value * qty_prop

    # Account for servings per recipe, round all values
    # to ones' place and calculate total mass
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

    context['nutr_basic'] = nutr_basic_g
    context['nutr_other'] = nutr_other_mg
    context['energy_basic'] = energy_basic
    context['mass_basic'] = mass_basic

    recipe.calories_tot = energy_basic['energy_tot']
    recipe.save()

    return render_to_response('recipe_update.html', context,
                              context_instance=RequestContext(request))


def RecipeCreateFunc(request):

    owner = str(request.user.username)
    recipe = Recipe.objects.create(owner=owner)
    url = reverse('recipe_update', args=([recipe.id]))

    return HttpResponseRedirect(url)


def recipe_attr_edit_func(request, pk):

    attr = request.GET.get('attr', '')
    new_value = request.GET.get('new_value', '')
    recipe = Recipe.objects.get(pk=pk)

    setattr(recipe, attr, new_value)

    recipe.save()

    return HttpResponse(status=200)


def recipe_attr_edit_func2(request, pk):

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


# ---- Recipe Detail ------------------------------------------------
def RecipeDetailView(request, pk):

    context = {}

    recipe = Recipe.objects.get(pk=pk)
    context['recipe_v'] = recipe

    active = request.user.is_authenticated()
    context['active'] = active

    # Get vote_state ------------------------------------------------
    if active:
        h_temp = "_".join([str(pk), str(request.user.username)])
        vote, created = Vote.objects.get_or_create(recipe=recipe,
                                                   handle=h_temp)

        if created:
            return HttpResponseRedirect('/vote_stats_func/%s' % pk)

        context['vote_v'] = vote

    else:
        context['vote_v'] = 2

    # Get vote stats ------------------------------------------------
    vote_stat, created = VoteStat.objects.get_or_create(recipe=recipe)

    context['vote_stat_v'] = vote_stat

    # Retrieve old comments -----------------------------------------
    old_comments = Comment.objects.filter(recipe=recipe)
    context['old_comments_v'] = old_comments

    # Show empty form for new comments, process new comments --------
    if active:
        context['comments_v'] = CommentForm(initial={'recipe': pk})
        if request.method == 'POST':
            from_form = CommentForm(request.POST)

            if from_form.is_valid():
                new_comment = from_form.save()

                user_name = request.user.username
                time = str(new_comment.time_stamp)

                # Because comments might get moderated, a given comment-number
                # might not match the total number of allowed comments
                # preceding it (ie, if there are 10 comments, the next comment
                # will be #11 [ie, 10 + 1] but if #2 is deleted by the admin,
                # the subsequent comment should be #12 even though there are
                # only 11 comments in the list.
                length = len(old_comments)
                if length == 1:
                    number = length
                else:
                    number = old_comments[length - 2].number + 1

                new_comment.user_name = user_name
                new_comment.handle = "_".join([str(pk), user_name, time])
                new_comment.number = number
                new_comment.email = request.user.email
                new_comment.save()

                return HttpResponseRedirect('/recipe_detail/%s/' % pk)
            else:
                context['errors'] = new_comment.errors

    # Send data to template -----------------------------------------
    return render_to_response('recipe_detail.html', context,
                              context_instance=RequestContext(request))


# ---- Add, Edit, and Delete Recipes (models.py Recipe) -------------
def recipe_add(request):

    context = {}

    form = RecipeAddForm()
    context['form_recipe_add'] = form

    if request.method == 'POST':
        form = RecipeAddForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/recipe_list/')
        else:
            context['errors'] = form.errors

    return render_to_response('recipe_add.html', context,
                              context_instance=RequestContext(request))


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


def recipe_del_func(request, pk):

    Recipe.objects.get(pk=pk).delete()

    return HttpResponseRedirect('/recipe_list/')


def recipe_del_page(request, pk):

    context = {}

    context['recipe_del'] = Recipe.objects.get(pk=pk)

    return render_to_response('recipe_del_page.html', context,
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


# ---- Voting Recipes Up or Down ------------------------------------
# If user has never voted, upvote makes their vote = +1;
# If they have voted before & their vote == +1, upvote makes vote = 0;
# ... if their vote was 0 or -1, upvote makes their vote = +1
# Likewise for downvotes (with appropriate changes in sign)
def vote_up_func(request, pk):

    h_temp = "_".join([str(pk), str(request.user)])
    vote_cur = Vote.objects.get(handle=h_temp)

    if vote_cur.state == 1:
        vote_cur.state = 0

    else:
        vote_cur.state = 1

    vote_cur.save()

    return HttpResponseRedirect('/vote_stats_func/%s' % pk)


def vote_dn_func(request, pk):

    h_temp = "_".join([str(pk), str(request.user)])
    vote_cur = Vote.objects.get(handle=h_temp)

    if vote_cur.state == -1:
        vote_cur.state = 0

    else:
        vote_cur.state = -1

    vote_cur.save()

    return HttpResponseRedirect('/vote_stats_func/%s' % pk)


def vote_stats_func(request, pk):

    # Count votes for the given Recipe ------------------------------
    upvote_sum = len(Vote.objects.filter(recipe=pk, state=1))
    dnvote_sum = len(Vote.objects.filter(recipe=pk, state=-1))
    totvote_sum = upvote_sum + dnvote_sum

    # Save stats to VoteStat model ----------------------------------
    vote_stat, created = VoteStat.objects.get_or_create(recipe_id=pk)

    vote_stat.v_up = upvote_sum
    vote_stat.v_dn = dnvote_sum
    vote_stat.v_tot = totvote_sum

    if totvote_sum == 0:
        vote_stat.v_up_p = 0.0
        vote_stat.v_dn_p = 0.0
    else:
        vote_stat.v_up_p = upvote_sum * 100 / totvote_sum
        vote_stat.v_dn_p = dnvote_sum * 100 / totvote_sum

    vote_stat.save()

    return HttpResponseRedirect('/recipe_detail/%s' % pk)
