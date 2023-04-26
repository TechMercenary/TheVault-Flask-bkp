from models import db, AccountType
from app_build import app
from flask import render_template, request, url_for, redirect


@app.route('/account_type/')
def account_type_index():
    account_types = AccountType.query.order_by(AccountType.name).all()
    return render_template(
        'tables/account_type/account_type_index.html',
        account_types=account_types,
    )


@app.route('/account_type/create/', methods=['GET', 'POST'])
def account_type_create():
    if request.method == 'POST':
        
        name = request.form['name'].upper().strip()
        description = request.form['description'].strip() if request.form['description'] else None
        normal_side = request.form['normal_side'].strip()
        
        db.session.add(AccountType(
            name=name,
            description=description,
            normal_side=normal_side,
        ))
        db.session.commit()
        return redirect(url_for('account_type_index'))

    return render_template(
        'tables/account_type/account_type_create.html',
    )


@app.route('/account_type/<int:account_type_id>/edit/', methods=['GET', 'POST'])
def account_type_edit(account_type_id):
    account_type = AccountType.query.get_or_404(account_type_id)

    if request.method == 'POST':
        account_type.name = request.form['name'].upper().strip()
        account_type.description = request.form['description'].strip() if request.form['description'] else None
        account_type.normal_side = request.form['normal_side'].strip()
        
        db.session.add(account_type)
        db.session.commit()
        return redirect(url_for('account_type_index'))
    
    return render_template(
        'tables/account_type/account_type_edit.html',
        account_type=account_type,
    )


@app.route('/account_type/<int:account_type_id>/delete/', methods=['GET', 'POST'])
def account_type_delete(account_type_id):
    db.session.delete(AccountType.query.get_or_404(account_type_id))
    db.session.commit()
    
    return redirect(url_for('account_type_index'))
