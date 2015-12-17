from django import forms
from django.core.urlresolvers import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout, Div
from crispy_forms.bootstrap import FormActions

from main.models import Recipe, IngredNutr, Comment


# ---- Add a Recipe to the Database ---------------------------------
class RecipeAddForm(forms.ModelForm):

    class Meta:
        model = Recipe
        fields = '__all__'
        labels = {
                  'ingred': 'Ingredient',
                  'name': 'Recipe Name',
                  'description': 'Description',
                  'category': 'Category',
                  'tags': 'Tags',
                  'time_prep': 'Preparation Time',
                  'time_cook': 'Cook Time',
                  'time_tot': 'Total Time',
                  'directions': 'Instructions',
                  'author': 'Recipe Creator',
                  'owner': 'Recipe Manager',
                  'image': 'Image',
                  }

    def __init__(self, *args, **kwargs):
        super(RecipeAddForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = '/recipe_add/'
        self.helper.layout.append(
            FormActions(
                Submit('add_new_recipe', 'Add new recipe',
                       css_class="btn-primary"),
                )
            )


# ---- Edit a Recipe in the Database --------------------------------
class RecipeEditForm(forms.ModelForm):

    class Meta:
        model = Recipe
        fields = '__all__'
        # labels = {
        #           'name': 'Recipe Name',
        #           'description': 'Description',
        #           'category': 'Category',
        #           'tags': 'Tags',
        #           'time_prep': 'Preparation Time',
        #           'time_cook': 'Cook Time',
        #           'time_tot': 'Total Time',
        #           'directions': 'Instructions',
        #           'author': 'Recipe Creator',
        #           'owner': 'Recipe Manager',
        #           'image': 'Image',
        #           }

    def __init__(self, *args, **kwargs):
        super(RecipeEditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = '/recipe_edit/%s/' % self.instance.pk
        self.helper.layout.append(
            FormActions(
                Submit('save_changes_to_recipe', 'Save changes to recipe',
                       css_class="btn-primary"),
                )
            )


# ---- Add an Ingredient to the Database ----------------------------
class IngredAddForm(forms.ModelForm):

    class Meta:
        model = IngredNutr
        fields = '__all__'
        labels = {
                  'name': 'Ingredient Name',
                  'recipe': 'Recipes which use it',
                  'image': 'Image',
                  'wiki_link': 'Wikipedia Link',
                  }

    def __init__(self, *args, **kwargs):
        super(IngredAddForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = '/ingred_add/'
        self.helper.layout.append(
            FormActions(
                Submit('add_new_ingred', 'Add new ingredient',
                       css_class="btn-primary"),
                )
            )


# ---- Sign Up / In / Out -------------------------------------------
class UserSignUp(forms.Form):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    name = forms.CharField(required=True)
    email = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput())


class UserSignIn(forms.Form):
    name = forms.CharField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput())


# ---- Comments on Recipes ------------------------------------------
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'recipe']
        widgets = {'recipe': forms.HiddenInput()}
        labels = {'text': 'Comment'}

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = ''

        self.helper.layout = Layout('text')
        self.helper.layout.append(
            FormActions(
                        Submit('add_comment',
                               'Add Comment',
                               css_class="btn-primary"
                               )
                        )
        )


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['image']

    def __init__(self, *args, **kwargs):
        super(UploadImageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = ''

        self.helper.layout = Layout('image')
        self.helper.layout.append(
            FormActions(
                        Submit('upload_image',
                               'Upload Image',
                               css_class="btn-primary"
                               )
                        )
        )
