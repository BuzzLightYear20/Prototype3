from flask import render_template, request, jsonify, flash, redirect, url_for, session, current_app
from flask_babel import get_locale
from flask.blueprints import Blueprint
from flask_login import current_user, login_required
from app import db
from app.models import Term, Suggestion, Language
from app.forms import SuggestionForm
import random

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Home')

@bp.route('/dictionary')
def dictionary():
    query = request.args.get('query', '').lower()
    category = request.args.get('category', 'All')
    q = Term.query
    if category != 'All':
        q = q.filter(Term.category == category)
    if query:
        q = q.filter(Term.term.ilike(f'%{query}%'))
    terms = q.order_by(Term.term).all()
    categories = ['All'] + sorted(list(set(t.category for t in Term.query.all())))
    favorite_ids = [term.id for term in current_user.favorite_terms] if current_user.is_authenticated else []
    current_lang_code = str(get_locale())
    return render_template('dictionary.html', title='Dictionary', terms=terms, categories=categories,
                           selected_category=category, favorite_ids=favorite_ids, current_lang=current_lang_code)

@bp.route('/favorites')
@login_required
def favorites():
    terms = current_user.favorite_terms.order_by(Term.term).all()
    current_lang_code = str(get_locale())
    return render_template('favorites.html', title='My Favorites', terms=terms, current_lang=current_lang_code)

@bp.route('/toggle_favorite/<int:term_id>', methods=['POST'])
@login_required
def toggle_favorite(term_id):
    term = Term.query.get_or_404(term_id)
    if term in current_user.favorite_terms:
        current_user.favorite_terms.remove(term)
    else:
        current_user.favorite_terms.append(term)
    db.session.commit()
    return jsonify({'status': 'ok'})

@bp.route('/quiz')
@login_required
def quiz():
    current_lang_code = str(get_locale())
    terms_with_translation = Term.query.join(Term.translations).join(Translation.language).filter(Language.code == current_lang_code).all()
    if len(terms_with_translation) < 4:
        flash('Not enough translated terms in the current language to start a quiz.')
        return redirect(url_for('main.dictionary'))
    question_term = random.choice(terms_with_translation)
    options = [question_term]
    while len(options) < 4:
        option = random.choice(terms_with_translation)
        if option not in options:
            options.append(option)
    random.shuffle(options)
    return render_template('quiz.html', title='Quiz', question=question_term, options=options, current_lang=current_lang_code)

@bp.route('/suggest', methods=['GET', 'POST'])
@login_required
def suggest():
    form = SuggestionForm()
    form.language.choices = [(lang.id, lang.name) for lang in Language.query.order_by('name').all()]
    if form.validate_on_submit():
        language = Language.query.get(form.language.data)
        suggestion = Suggestion(
            term=form.term.data,
            category=form.category.data,
            definition=form.definition.data,
            language_name=language.name,
            submitted_by=current_user.username
        )
        db.session.add(suggestion)
        db.session.commit()
        flash('Your suggestion has been submitted for review!', 'success')
        return redirect(url_for('main.dictionary'))
    return render_template('suggest.html', title='Suggest a Term', form=form)

@bp.route('/language/<language>')
def set_language(language=None):
    if language in current_app.config['LANGUAGES']:
        session['language'] = language
    return redirect(request.referrer or url_for('main.index'))