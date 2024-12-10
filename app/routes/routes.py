from app.controllers.faq_controller import faq
from app.controllers.register_controller import register
from app.controllers.report_controller import report
from app.controllers.home_controller import home
from app.controllers.generate_controller import generate
from app.controllers.feedback_controller import analyze_feedbacks
from app.controllers.faq_controller import faq, add_faq, delete_faq
from app.controllers.feedback_controller import render_feedback_form, submit_feedback
from app.controllers.admin_controller import admin_feedback_summary

def initialize_routes(app):
    app.add_url_rule('/', 'home', home, methods=['GET'])
    app.add_url_rule('/faq', 'faq', faq, methods=['GET', 'POST'])
    app.add_url_rule('/faq/add', 'add_faq', add_faq, methods=['POST'])
    app.add_url_rule('/faq/delete', 'delete_faq', delete_faq, methods=['DELETE'])
    app.add_url_rule('/register', 'register', register, methods=['POST'])
    app.add_url_rule('/report', 'report', report, methods=['GET'])
    app.add_url_rule('/generate', 'generate', generate, methods=['POST'])
    app.add_url_rule('/feedback/analyze', 'analyze_feedbacks', analyze_feedbacks, methods=['POST'])
    app.add_url_rule('/feedback', 'render_feedback_form', render_feedback_form, methods=['GET'])
    app.add_url_rule('/feedback/submit', 'submit_feedback', submit_feedback, methods=['POST'])
    app.add_url_rule('/admin/feedback-summary', 'admin_feedback_summary', admin_feedback_summary, methods=['GET'])