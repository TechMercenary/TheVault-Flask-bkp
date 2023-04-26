from models import db, Currency, Account, AccountGroup, AccountType
from app_build import app
from flask import render_template, request, url_for, redirect
import pendulum


@app.route('/account/')
def account_index():
    accounts = sorted(Account.query.all(), key=lambda x: x.alias.lower())
    return render_template(
        'tables/account/account_index.html',
        accounts=accounts,
    )


@app.route('/account/create/', methods=['GET', 'POST'])
def account_create():
    if request.method == 'POST':
        
        name = request.form['name'].strip()
        description = request.form['description'].strip() if request.form['description'] else None
        number = request.form['number'].strip() if request.form['number'] else None
        currency_id = request.form['currency_id']
        account_group_id = request.form['account_group_id']
        account_type_id = request.form['account_type_id']
        
        opened_at = pendulum.datetime(
            year=int(request.form['opened_at_year']),
            month=int(request.form['opened_at_month']),
            day=int(request.form['opened_at_day']),
            hour=int(request.form['opened_at_hour']),
            minute=int(request.form['opened_at_minute']),
            tz='America/Argentina/Buenos_Aires',
        ).to_datetime_string()
        
        try:
            closed_at = pendulum.datetime(
                year=int(request.form['closed_at_year']),
                month=int(request.form['closed_at_month']),
                day=int(request.form['closed_at_day']),
                hour=int(request.form['closed_at_hour']),
                minute=int(request.form['closed_at_minute']),
                tz='America/Argentina/Buenos_Aires',
            ).to_datetime_string()
        except Exception:
            closed_at = None
        
        db.session.add(Account(
            name=name,
            description=description,
            number=number,
            currency_id=currency_id,
            opened_at=opened_at,
            closed_at=closed_at,
            account_group_id=account_group_id,
            account_type_id=account_type_id,
        ))
        db.session.commit()
        return redirect(url_for('account_index'))

    currencies = Currency.query.order_by(Currency.code).all()
    account_groups = sorted(AccountGroup.query.all(), key=lambda x: x.alias.lower())
    account_types = sorted(AccountType.query.all(), key=lambda x: x.name.lower())

    return render_template(
        'tables/account/account_create.html',
        currencies=currencies,
        account_groups=account_groups,
        account_types=account_types,
        current_year=pendulum.now().year,
        current_month=pendulum.now().month,
        current_day=pendulum.now().day,
        current_hour=pendulum.now().hour,
        current_minute=pendulum.now().minute,
    )


@app.route('/account/<int:account_id>/edit/', methods=['GET', 'POST'])
def account_edit(account_id):
    account = Account.query.get_or_404(account_id)

    if request.method == 'POST':

        name = request.form['name'].strip()
        description = request.form['description'].strip() if request.form['description'] else None
        number = request.form['number'].strip() if request.form['number'] else None
        currency_id = request.form['currency_id']
        account_group_id = request.form['account_group_id']
        account_type_id = request.form['account_type_id']

        opened_at = pendulum.datetime(
            year=int(request.form['opened_at_year']),
            month=int(request.form['opened_at_month']),
            day=int(request.form['opened_at_day']),
            hour=int(request.form['opened_at_hour']),
            minute=int(request.form['opened_at_minute']),
            tz='America/Argentina/Buenos_Aires',
        ).to_datetime_string()
        
        try:
            closed_at = pendulum.datetime(
                year=int(request.form['closed_at_year']),
                month=int(request.form['closed_at_month']),
                day=int(request.form['closed_at_day']),
                hour=int(request.form['closed_at_hour']),
                minute=int(request.form['closed_at_minute']),
                tz='America/Argentina/Buenos_Aires',
            ).to_datetime_string()
        except Exception:
            closed_at = None

        account.name = name
        account.description = description
        account.number = number
        account.currency_id = currency_id
        account.opened_at = opened_at
        account.closed_at = closed_at
        account.account_group_id = account_group_id
        account.account_type_id = account_type_id
        
        db.session.add(account)
        db.session.commit()
        return redirect(url_for('account_index'))
    
    currencies = Currency.query.order_by(Currency.code).all()
    account_groups = sorted(AccountGroup.query.all(), key=lambda x: x.alias.lower())
    account_types = sorted(AccountType.query.all(), key=lambda x: x.name.lower())
    
    opened_at = pendulum.parse(str(account.opened_at)) # type: ignore
    closed_at = pendulum.parse(str(account.closed_at)) if account.closed_at else None # type: ignore
    return render_template(
        'tables/account/account_edit.html',
        account=account,
        currencies=currencies,
        account_groups=account_groups,
        account_types=account_types,
        opened_at_year=opened_at.year,   # type: ignore
        opened_at_month=opened_at.month,  # type: ignore
        opened_at_day=opened_at.day,   # type: ignore
        opened_at_hour=opened_at.hour,  # type: ignore
        opened_at_minute=opened_at.minute,  # type: ignore
        closed_at_year=getattr(closed_at,'year', None),
        closed_at_month=getattr(closed_at,'month', None),
        closed_at_day=getattr(closed_at,'day', None),
        closed_at_hour=getattr(closed_at,'hour', None),
        closed_at_minute=getattr(closed_at,'minute', None),
    )


@app.route('/account/<int:account_id>/delete/', methods=['GET', 'POST'])
def account_delete(account_id):
    db.session.delete(Account.query.get_or_404(account_id))
    db.session.commit()
    
    return redirect(url_for('account_index'))
