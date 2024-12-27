from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from app import db

class Evenement(db.Model):
    __tablename__ = 'evenements'

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=True)

    conferences = db.relationship('Conference', backref='evenement', lazy=True)
    feedbacks = db.relationship('Feedback', backref='evenement', lazy=True)
    Visuals = db.relationship('Visual', backref='evenement', lazy=True)

    def __repr__(self):
        return f"<Evenement {self.titre}>"


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='participant')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    participant_name = db.Column(db.String(255), nullable=False)
    participant_email = db.Column(db.String(255), nullable=True)
    feedback_text = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    evenement_id = db.Column(db.Integer, db.ForeignKey('evenements.id'), nullable=True)

class Participant(db.Model):
    __tablename__ = 'participants'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    nom = db.Column(db.String(255), nullable=False)
    prenom = db.Column(db.String(255), nullable=False)
    sexe = db.Column(db.String(50), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    profession = db.Column(db.String(255), nullable=False)

    conferences = db.relationship(
        'Conference', secondary='participant_conferences', back_populates='participants'
    )

class Speaker(db.Model):
    __tablename__ = 'speakers'

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(255), nullable=False)
    prenom = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    sexe = db.Column(db.String(50), nullable=True)
    profession = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text, nullable=True)

    conferences = db.relationship('Conference', back_populates='speaker')

class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=True)  # 'marketing', 'recap', 'announcement', etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    conference_id = db.Column(db.Integer, db.ForeignKey('conferences.id'), nullable=True)
    evenement_id = db.Column(db.Integer, db.ForeignKey('evenements.id'), nullable=True)

    def __repr__(self):
        return f"<Article {self.title}>"

class Conference(db.Model):
    __tablename__ = 'conferences'

    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String(255), nullable=False)
    speaker_id = db.Column(db.Integer, db.ForeignKey('speakers.id'), nullable=False)
    horaire = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=True)
    evenement_id = db.Column(db.Integer, db.ForeignKey('evenements.id'), nullable=True)

    # Relations
    speaker = db.relationship('Speaker', back_populates='conferences')
    participants = db.relationship(
        'Participant', secondary='participant_conferences', back_populates='conferences'
    )
    articles = db.relationship('Article', backref='conference', lazy=True)

participant_conferences = db.Table(
    'participant_conferences',
    db.Column('participant_id', db.Integer, db.ForeignKey('participants.id'), primary_key=True),
    db.Column('conference_id', db.Integer, db.ForeignKey('conferences.id'), primary_key=True)
)

class Visual(db.Model):
    __tablename__ = 'visuals'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    associated_type = db.Column(db.String(50), nullable=True)  # 'conference' ou 'article'
    associated_id = db.Column(db.Integer, nullable=True)  # ID de la conférence ou de l'article associé
    evenement_id = db.Column(db.Integer, db.ForeignKey('evenements.id'), nullable=True)

    def __repr__(self):
        return f"<Visual {self.title}>"