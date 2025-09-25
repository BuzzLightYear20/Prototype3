from flask import Flask, request, session, current_app
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_babel import Babel, get_locale
from flask_admin import Admin

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
babel = Babel()
admin_panel = Admin(name='ALA Admin', template_mode='bootstrap4')

def select_locale():
    if 'language' in session:
        return session['language']
    return request.accept_languages.best_match(current_app.config.get('LANGUAGES', ['en']))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    babel.init_app(app, locale_selector=select_locale)
    admin_panel.init_app(app)

    from app.models import User, Term, Suggestion, Language, Translation
    from app.admin import UserAdminView, TermAdminView, SuggestionAdminView, LanguageAdminView, TranslationAdminView
    
    admin_panel.add_view(UserAdminView(User, db.session, category="Management"))
    admin_panel.add_view(LanguageAdminView(Language, db.session, category="Management"))
    admin_panel.add_view(TermAdminView(Term, db.session, category="Content"))
    admin_panel.add_view(TranslationAdminView(Translation, db.session, category="Content"))
    admin_panel.add_view(SuggestionAdminView(Suggestion, db.session, category="Content"))

    with app.app_context():
        try:
            app.config['LANGUAGES'] = [lang.code for lang in Language.query.all()]
        except Exception:
            app.config['LANGUAGES'] = ['en']

    @app.context_processor
    def inject_globals():
        return {'get_locale': get_locale}

    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app

from app import models