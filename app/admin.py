from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for
from flask_admin.form import BaseForm
# Import all necessary field types from the correct library
from wtforms import StringField, PasswordField, BooleanField, TextAreaField
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import Language, Term

# --- CUSTOM FORMS FOR EVERY ADMIN VIEW ---

# This form is for creating/editing Users
class UserAdminForm(BaseForm):
    username = StringField('Username')
    email = StringField('Email')
    is_admin = BooleanField('Is Admin')
    password = PasswordField('New Password (leave blank to keep current)')

# This form is for creating/editing Languages
class LanguageAdminForm(BaseForm):
    name = StringField('Name (e.g., English)')
    code = StringField('Code (e.g., en)')

# This form is for creating/editing Terms
class TermAdminForm(BaseForm):
    term = StringField('Term')
    category = StringField('Category')

# This form is for creating/editing Translations
class TranslationAdminForm(BaseForm):
    language = QuerySelectField(query_factory=lambda: Language.query.all(), get_label='name', allow_blank=False)
    term = QuerySelectField(query_factory=lambda: Term.query.all(), get_label='term', allow_blank=False)
    definition = TextAreaField('Definition', render_kw={"rows": 5})

# --- SECURE MODEL VIEW ---
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))

# --- ADMIN VIEWS USING THE CORRECT CUSTOM FORMS ---
class UserAdminView(SecureModelView):
    form = UserAdminForm
    column_list = ('username', 'email', 'is_admin')
    column_searchable_list = ('username', 'email')
    column_filters = ('is_admin',)

    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.set_password(form.password.data)

class LanguageAdminView(SecureModelView):
    form = LanguageAdminForm
    column_list = ('name', 'code')
    column_searchable_list = ('name', 'code')

class TermAdminView(SecureModelView):
    form = TermAdminForm
    column_list = ('term', 'category')
    column_searchable_list = ('term', 'category')
    column_filters = ('category',)

class TranslationAdminView(SecureModelView):
    form = TranslationAdminForm
    column_list = ('term', 'language', 'definition')
    column_searchable_list = ('term.term', 'language.name', 'definition')
    column_filters = ('language', 'term')

class SuggestionAdminView(SecureModelView):
    # Suggestions are read-only in the admin panel, so no custom form is needed.
    can_create = False
    can_edit = False
    column_list = ('term', 'category', 'language_name', 'submitted_by', 'is_approved')
    column_searchable_list = ('term', 'submitted_by')
    column_filters = ('is_approved', 'language_name')