import requests

from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import RequestContext

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from main.forms import RecipeAddForm, RecipeEditForm
from main.forms import IngredAddForm
from main.forms import UserSignUp, UserSignIn
from main.forms import CommentForm

from main.models import IngredNDB, IngredNutr, Recipe
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


# ---- IngredNDB Detail ---------------------------------------------
def IngredNDBDetailView(request, pk):

    context = {}

    ingred = IngredNDB.objects.get(pk=pk)
    context['ingred_v'] = ingred

    nutr_list = NDBQuery(ingred.ndb_no)

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

    #  Initialize the variables
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
        # print "nutr_id: %s" % nutr_id

        # print "nutr_id_list: %s" % nutrient_id_list
        if nutrient_id_list == []:
            break

        if nutr_id in nutrient_id_list:
            # print "checkpoint 1"
            if nutr_id == 255:
                water = float(nutr['value'])
                nutrient_id_list.remove(nutr_id)
                # print "water: %s" % water

            elif nutr_id == 203:
                protein = float(nutr['value'])
                nutrient_id_list.remove(nutr_id)

            elif nutr_id == 204:
                lipids = float(nutr['value'])
                nutrient_id_list.remove(nutr_id)

            elif nutr_id == 205:
                carbs = float(nutr['value'])
                nutrient_id_list.remove(nutr_id)
                # print "carbs: %s" % carbs

            elif nutr_id == 291:
                fiber = float(nutr['value'])
                nutrient_id_list.remove(nutr_id)

            elif nutr_id == 269:
                sugars = float(nutr['value'])
                nutrient_id_list.remove(nutr_id)
                # print "sugars: %s" % sugars

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

    return render_to_response('ingred_ndb_detail.html', context,
                              context_instance=RequestContext(request))


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


#  ---- Adding Ingredients to a Recipe ------------------------------
def json_response(request):
    search_string = request.GET.get('search', '')

    objects = IngredNDB.objects.filter(
        ndb_description__icontains=search_string
        )

    object_list = []
    for obj in objects:
        object_list.append(obj.ndb_description)

    return JsonResponse(object_list, safe=False)


def json_measures(request):
    search_string = request.GET.get('search2', '')

    print search_string
    objects = IngredNutr.objects.filter(
        handle__icontains=search_string
        )

    object_list = []
    for obj in objects:
        object_list.append(obj.label)

    return JsonResponse(object_list, safe=False)


def Temp(request):

    context = {}

    return render_to_response('temp.html', context,
                              context_instance=RequestContext(request))
