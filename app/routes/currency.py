from models import db, Currency
from app_build import app
from flask import render_template, request, url_for, redirect


@app.route('/currency/')
def currency_index():
    currencies = Currency.query.order_by(Currency.code).all()
    return render_template(
        'tables/currency/currency_index.html',
        currencies=currencies,
    )


@app.route('/currency/create/', methods=['GET', 'POST'])
def currency_create():
    if request.method == 'POST':
        
        code = request.form['code'].upper().strip()
        description = request.form['description'].strip() if request.form['description'] else None
        
        db.session.add(Currency(
            code=code,
            description=description,
        ))
        db.session.commit()
        return redirect(url_for('currency_index'))

    return render_template(
        'tables/currency/currency_create.html',
    )


@app.route('/currency/<int:currency_id>/edit/', methods=['GET', 'POST'])
def currency_edit(currency_id):
    currency = Currency.query.get_or_404(currency_id)

    if request.method == 'POST':
        currency.code = request.form['code'].upper().strip()
        currency.description = request.form['description'].strip() if request.form['description'] else None
        db.session.add(currency)
        db.session.commit()
        return redirect(url_for('currency_index'))
    return render_template(
        'tables/currency/currency_edit.html',
        currency=currency,
    )


@app.route('/currency/<int:currency_id>/delete/', methods=['GET', 'POST'])
def currency_delete(currency_id):
    db.session.delete(Currency.query.get_or_404(currency_id))
    db.session.commit()
    
    return redirect(url_for('currency_index'))
