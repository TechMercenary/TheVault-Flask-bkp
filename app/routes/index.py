from flask import render_template, request, url_for, redirect
from models import db
from app_build import app


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/employer')
def employer_index():
    return render_template('index.html')

@app.route('/salary')
def salary_index():
    return render_template('index.html')

@app.route('/credit_card')
def credit_card_index():
    return render_template('index.html')

@app.route('/credit_card_summary')
def credit_card_summary_index():
    return render_template('index.html')
