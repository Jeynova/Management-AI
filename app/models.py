from app import db
from datetime import datetime

class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    participant_name = db.Column(db.String(255), nullable=False)
    participant_email = db.Column(db.String(255), nullable=True)
    feedback_text = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Feedback {self.participant_name} ({self.sentiment})>"
    
class Participant(db.Model):
    __tablename__ = 'participants'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    nom = db.Column(db.String(255), nullable=False)
    prenom = db.Column(db.String(255), nullable=False)
    sexe = db.Column(db.String(50), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    profession = db.Column(db.String(255), nullable=False)

    # Relation avec les conférences via une table d'association
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

    # Relation avec les conférences
    conferences = db.relationship('Conference', back_populates='speaker')


class Conference(db.Model):
    __tablename__ = 'conferences'

    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String(255), nullable=False)
    speaker_id = db.Column(db.Integer, db.ForeignKey('speakers.id'), nullable=False)
    horaire = db.Column(db.DateTime, nullable=False)

    # Relations
    speaker = db.relationship('Speaker', back_populates='conferences')
    participants = db.relationship(
        'Participant', secondary='participant_conferences', back_populates='conferences'
    )


# Table d'association entre les participants et les conférences
participant_conferences = db.Table(
    'participant_conferences',
    db.Column('participant_id', db.Integer, db.ForeignKey('participants.id'), primary_key=True),
    db.Column('conference_id', db.Integer, db.ForeignKey('conferences.id'), primary_key=True)
)