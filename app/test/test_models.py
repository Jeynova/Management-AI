import pytest
from app import create_app, db
from app.models import Participant, Speaker, Conference
from datetime import datetime

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Base de données en mémoire pour les tests
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_models(app):
    with app.app_context():
        # Ajouter un participant
        participant = Participant(
            email="john.doe@example.com",
            nom="Doe",
            prenom="John",
            sexe="Homme",
            age=30,
            profession="Développeur"
        )
        db.session.add(participant)

        # Ajouter un speaker
        speaker = Speaker(
            nom="Smith",
            prenom="Alice",
            age=45,
            sexe="Femme",
            profession="Professeur"
        )
        db.session.add(speaker)

        # Ajouter une conférence
        conference = Conference(
            theme="Intelligence Artificielle",
            speaker=speaker,
            horaire=datetime(2024, 12, 25, 14, 30)
        )
        db.session.add(conference)

        # Lier un participant à une conférence
        conference.participants.append(participant)
        db.session.commit()

        # Vérifier les données
        assert Participant.query.count() == 1
        assert Speaker.query.count() == 1
        assert Conference.query.count() == 1
        assert conference.participants[0].nom == "Doe"