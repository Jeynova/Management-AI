from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email

class FeedbackForm(FlaskForm):
    name = StringField('Nom', validators=[DataRequired()])
    email = StringField('Email', validators=[Email()])
    feedback = TextAreaField('Votre avis', validators=[DataRequired()])
    submit = SubmitField('Envoyer')