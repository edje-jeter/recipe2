from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^about/$', 'main.views.about_view', name='about'),

    url(r'^get_ingred_ndb_json/$', 'main.views.get_ingred_ndb_json', name='get_ingred_ndb_json'),
    url(r'^json_ingred_nutr/$', 'main.views.JsonIngredNutr', name='json_ingred_nutr'),

    url(r'^ingred_ndb_list/$', 'main.views.IngredNDBListView', name='ingred_ndb_list'),
    url(r'^ingred_ndb_detail/(?P<pk>\d+)/$', 'main.views.IngredNDBDetailView', name='ingred_ndb_detail'),

    url(r'^ingred_add/$', 'main.views.ingred_add', name='ingred_add'),
    url(r'^ingred_del_func/(?P<pk>\d+)/$', 'main.views.ingred_del_func', name='ingred_del_func'),
    url(r'^ingred_del_page/(?P<pk>\d+)/$', 'main.views.ingred_del_page', name='ingred_del_page'),

    url(r'^recipe_list/$', 'main.views.RecipeListView', name='recipe_list'),
    url(r'^recipe_detail/(?P<pk>\d+)/$', 'main.views.recipe_detail', name='recipe_detail'),
    url(r'^recipe_attr_edit_func/(?P<pk>\d+)/$', 'main.views.recipe_attr_edit_func', name='recipe_attr_edit_func'),
    url(r'^add_quantity/(?P<pk>\d+)/$', 'main.views.add_quantity', name='add_quantity'),
    url(r'^del_quantity/$', 'main.views.del_quantity', name='del_quantity'),
    # url(r'^upload_image/(?P<pk>\d+)/$', 'main.views.upload_image', name='upload_image'),

    url(r'^recipe_create/$', 'main.views.recipe_create_func', name='recipe_create'),
    url(r'^recipe_edit/(?P<pk>\d+)/$', 'main.views.recipe_edit', name='recipe_edit'),
    url(r'^recipe_delete_func/(?P<pk>\d+)/$', 'main.views.recipe_delete_func', name='recipe_delete_func'),
    url(r'^recipe_delete_page/(?P<pk>\d+)/$', 'main.views.recipe_delete_page', name='recipe_delete_page'),
    url(r'^activate_edit_flag/(?P<pk>\d+)/$', 'main.views.activate_edit_flag', name='activate_edit_flag'),

    url(r'^sign_up/$', 'main.views.sign_up', name='sign_up'),
    url(r'^sign_in/$', 'main.views.sign_in', name='sign_in_v'),
    url(r'^sign_out/$', 'main.views.sign_out', name='sign_out_v'),
    url(r'^user_del_page/$', 'main.views.user_del_page', name='user_del_page'),

    url(r'^rating_func/(?P<pk>\d+)/$', 'main.views.rating_func', name='rating_func'),
    url(r'^rating_stats_func/(?P<pk>\d+)/$', 'main.views.rating_stats_func', name='rating_stats_func'),

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
