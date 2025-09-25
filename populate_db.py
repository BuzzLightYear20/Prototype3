from app import create_app, db
from app.models import Term, User, Language, Translation

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
    print("Cleared and recreated all tables.")

    lang_en = Language(code='en', name='English')
    lang_fr = Language(code='fr', name='Français')
    db.session.add_all([lang_en, lang_fr])
    db.session.commit()
    print("Added Languages.")

    term1 = Term(term='Honour Council', category='Disciplinary Bodies')
    term2 = Term(term='AOD (Adult on Duty)', category='Acronyms and Jargon')
    db.session.add_all([term1, term2])
    db.session.commit()
    print("Added Terms.")

    translations = [
        Translation(term=term1, language=lang_en, definition='A student-led body.'),
        Translation(term=term1, language=lang_fr, definition='Un organe dirigé par des étudiants.'),
        Translation(term=term2, language=lang_en, definition='The designated staff member on duty.'),
        Translation(term=term2, language=lang_fr, definition="Le membre du personnel désigné de service.")
    ]
    db.session.add_all(translations)
    
    admin = User(username='admin', email='admin@ala.com', is_admin=True)
    admin.set_password('adminpass')
    db.session.add(admin)
    
    db.session.commit()
    print("Database has been successfully populated!")