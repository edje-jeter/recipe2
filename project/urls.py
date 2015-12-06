from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^recipe_update/(?P<pk>\d+)/$', 'main.views.RecipeUpdate', name='recipe_update'),
    url(r'^json_ingred_ndb/$', 'main.views.JsonIngredNDB', name='json_ingred_ndb'),
    url(r'^json_ingred_ndb_2/$', 'main.views.json_ingred_ndb_2', name='json_ingred_ndb_2'),
    url(r'^json_ingred_nutr/$', 'main.views.JsonIngredNutr', name='json_ingred_nutr'),

    url(r'^recipe_create/$', 'main.views.RecipeCreateFunc', name='recipe_create'),
    url(r'^recipe_attr_edit_func/(?P<pk>\d+)/$', 'main.views.recipe_attr_edit_func', name='recipe_attr_edit_func'),
    url(r'^recipe_attr_edit_func2/(?P<pk>\d+)/$', 'main.views.recipe_attr_edit_func2', name='recipe_attr_edit_func2'),

    url(r'^ingred_ndb_list/$', 'main.views.IngredNDBListView', name='ingred_ndb_list'),
    url(r'^ingred_ndb_detail/(?P<pk>\d+)/$', 'main.views.IngredNDBDetailView', name='ingred_ndb_detail'),
    url(r'^ingred_add/$', 'main.views.ingred_add', name='ingred_add'),
    url(r'^ingred_del_func/(?P<pk>\d+)/$', 'main.views.ingred_del_func', name='ingred_del_func'),
    url(r'^ingred_del_page/(?P<pk>\d+)/$', 'main.views.ingred_del_page', name='ingred_del_page'),

    url(r'^recipe_list/$', 'main.views.RecipeListView', name='recipe_list'),
    url(r'^recipe_detail/(?P<pk>\d+)/$', 'main.views.RecipeDetailView', name='recipe_detail'),
    url(r'^recipe_add/$', 'main.views.recipe_add', name='recipe_add'),
    url(r'^recipe_edit/(?P<pk>\d+)/$', 'main.views.recipe_edit', name='recipe_edit'),
    url(r'^recipe_del_func/(?P<pk>\d+)/$', 'main.views.recipe_del_func', name='recipe_del_func'),
    url(r'^recipe_del_page/(?P<pk>\d+)/$', 'main.views.recipe_del_page', name='recipe_del_page'),

    url(r'^sign_up/$', 'main.views.sign_up', name='sign_up'),
    url(r'^sign_in/$', 'main.views.sign_in', name='sign_in_v'),
    url(r'^sign_out/$', 'main.views.sign_out', name='sign_out_v'),
    url(r'^user_del_page/$', 'main.views.user_del_page', name='user_del_page'),

    url(r'^vote_up_func/(?P<pk>\d+)/$', 'main.views.vote_up_func', name='vote_up_func'),
    url(r'^vote_dn_func/(?P<pk>\d+)/$', 'main.views.vote_dn_func', name='vote_dn_func'),
    url(r'^vote_stats_func/(?P<pk>\d+)/$', 'main.views.vote_stats_func', name='vote_stats_func'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
