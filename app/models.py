from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('term_id', db.Integer, db.ForeignKey('term.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    favorite_terms = db.relationship('Term', secondary=favorites, backref='favorited_by', lazy='dynamic')

    def __str__(self):
        return self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(5), unique=True, nullable=False)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __str__(self):
        return self.name

class Term(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(100), index=True, unique=True, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    translations = db.relationship('Translation', back_populates='term', cascade="all, delete-orphan")

    def __str__(self):
        return self.term

    def get_translation(self, lang_code='en'):
        translation = next((t for t in self.translations if t.language.code == lang_code), None)
        if translation:
            return translation.definition
        english_translation = next((t for t in self.translations if t.language.code == 'en'), None)
        return english_translation.definition if english_translation else f"[{self.term} - No translation available]"

class Translation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    definition = db.Column(db.Text, nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('language.id'), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'), nullable=False)
    language = db.relationship('Language')
    term = db.relationship('Term', back_populates='translations')

    def __str__(self):
        return f"{self.term.term} ({self.language.code})"

class Suggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(100))
    category = db.Column(db.String(100))
    definition = db.Column(db.Text)
    language_name = db.Column(db.String(50))
    submitted_by = db.Column(db.String(100))
    is_approved = db.Column(db.Boolean, default=False)

    def __str__(self):
        return self.term