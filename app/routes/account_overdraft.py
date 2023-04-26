from models import db, AccountOverdraft, Account
from app_build import app
from flask import render_template, request, url_for, redirect
import pendulum
from decimal import Decimal

@app.route('/account_overdraft/')
def account_overdraft_index():
    account_overdrafts = sorted(AccountOverdraft.query.all(), key=lambda x: (x.account.alias.lower(), x.started_at), reverse=True)

    return render_template(
        'tables/account_overdraft/account_overdraft_index.html',
        account_overdrafts=account_overdrafts,
    )


@app.route('/account_overdraft/create/', methods=['GET', 'POST'])
def account_overdraft_create():
    if request.method == 'POST':
        
        account_id = request.form['account_id']
        started_at = pendulum.datetime(
            year=int(request.form['started_at_year']),
            month=int(request.form['started_at_month']),
            day=int(request.form['started_at_day']),
            hour=int(request.form['started_at_hour']),
            minute=int(request.form['started_at_minute']),
            tz='America/Argentina/Buenos_Aires',
        ).to_datetime_string()
        limit_amount = Decimal(request.form['limit_amount'])
        
        
        db.session.add(AccountOverdraft(
            account_id=account_id,
            started_at=started_at,
            limit_amount=limit_amount,
        ))
        db.session.commit()
        return redirect(url_for('account_overdraft_index'))

    accounts = sorted(Account.query.all(), key=lambda x: x.alias.lower())

    return render_template(
        'tables/account_overdraft/account_overdraft_create.html',
        accounts=accounts,
        current_year=pendulum.now().year,
        current_month=pendulum.now().month,
        current_day=pendulum.now().day,
        current_hour=pendulum.now().hour,
        current_minute=pendulum.now().minute,
    )


@app.route('/account_overdraft/<int:account_overdraft_id>/edit/', methods=['GET', 'POST'])
def account_overdraft_edit(account_overdraft_id):
    account_overdraft = AccountOverdraft.query.get_or_404(account_overdraft_id)

    if request.method == 'POST':
        account_id = request.form['account_id']
        started_at = pendulum.datetime(
            year=int(request.form['started_at_year']),
            month=int(request.form['started_at_month']),
            day=int(request.form['started_at_day']),
            hour=int(request.form['started_at_hour']),
            minute=int(request.form['started_at_minute']),
            tz='America/Argentina/Buenos_Aires',
        ).to_datetime_string()
        limit_amount = Decimal(request.form['limit_amount'])
        
        account_overdraft.account_id = account_id
        account_overdraft.started_at = started_at
        account_overdraft.limit_amount = limit_amount
        
        db.session.add(account_overdraft)
        db.session.commit()
        return redirect(url_for('account_overdraft_index'))
    
    accounts = sorted(Account.query.all(), key=lambda x: x.alias.lower())
    
    started_at = pendulum.parse(str(account_overdraft.started_at)) # type: ignore
    
    return render_template(
        'tables/account_overdraft/account_overdraft_edit.html',
        account_overdraft=account_overdraft,
        accounts=accounts,
        stated_at_year=started_at.year,  # type: ignore
        stated_at_month=started_at.month,  # type: ignore
        stated_at_day=started_at.day,  # type: ignore
        stated_at_hour=started_at.hour,  # type: ignore
        stated_at_minute=started_at.minute,  # type: ignore
    )


@app.route('/account_overdraft/<int:account_overdraft_id>/delete/', methods=['GET', 'POST'])
def account_overdraft_delete(account_overdraft_id):
    db.session.delete(AccountOverdraft.query.get_or_404(account_overdraft_id))
    db.session.commit()
    
    return redirect(url_for('account_overdraft_index'))
