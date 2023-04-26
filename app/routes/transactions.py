from models import db, Transaction, Account
from app_build import app
from flask import render_template, request, url_for, redirect
import pendulum
from decimal import Decimal


@app.route('/transaction/')
def transaction_index():
    transactions = Transaction.query.order_by(Transaction.created_at).all()
    return render_template(
        'tables/transaction/transaction_index.html',
        transactions=transactions,
    )


@app.route('/transaction/create/', methods=['GET', 'POST'])
def transaction_create():
    if request.method == 'POST':
        
        created_at = pendulum.datetime(
            year=int(request.form['created_at_year']),
            month=int(request.form['created_at_month']),
            day=int(request.form['created_at_day']),
            hour=int(request.form['created_at_hour']),
            minute=int(request.form['created_at_minute']),
            tz='America/Argentina/Buenos_Aires',
        ).to_datetime_string()
        description = request.form['description'].strip() if request.form['description'] else None
        # Installment
        installment_number = int(request.form['installment_number']) if request.form['installment_number'] else None
        installment_total = int(request.form['installment_total']) if request.form['installment_total'] else None
        # Debit
        debit_reference = request.form['debit_reference'].strip() if request.form['debit_reference'] else None
        debit_account_id = request.form['debit_account_id']
        debit_amount = Decimal(request.form['debit_amount'])
        # Credit
        credit_reference = request.form['credit_reference'].strip() if request.form['credit_reference'] else None
        credit_account_id = request.form['credit_account_id']
        credit_amount = Decimal(request.form['credit_amount'])

        db.session.add(Transaction(
            created_at=created_at,
            description=description,
            installment_number=installment_number,
            installment_total=installment_total,
            debit_reference=debit_reference,
            debit_account_id=debit_account_id,
            debit_amount=debit_amount,
            credit_reference=credit_reference,
            credit_account_id=credit_account_id,
            credit_amount=credit_amount,
            is_reconciled=False,
        ))
        db.session.commit()
        return redirect(url_for('transaction_index'))

    accounts = sorted(Account.query.all(), key=lambda x: x.alias)
    current_timestamp = pendulum.now('America/Argentina/Buenos_Aires')
    return render_template(
        'tables/transaction/transaction_create.html',
        accounts=accounts,
        current_year=current_timestamp.year,
        current_month=current_timestamp.month,
        current_day=current_timestamp.day,
        current_hour=current_timestamp.hour,
        current_minute=current_timestamp.minute,
    )


@app.route('/transaction/<int:transaction_id>/edit/', methods=['GET', 'POST'])
def transaction_edit(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)

    if request.method == 'POST':
        created_at = pendulum.datetime(
            year=int(request.form['created_at_year']),
            month=int(request.form['created_at_month']),
            day=int(request.form['created_at_day']),
            hour=int(request.form['created_at_hour']),
            minute=int(request.form['created_at_minute']),
            tz='America/Argentina/Buenos_Aires',
        ).to_datetime_string()
        description = request.form['description'].strip() if request.form['description'] else None
        is_reconciled = bool(request.form.get('is_reconciled'))
        # Installment
        installment_number = int(request.form['installment_number']) if request.form['installment_number'] else None
        installment_total = int(request.form['installment_total']) if request.form['installment_total'] else None
        # Debit
        debit_reference = request.form['debit_reference'].strip() if request.form['debit_reference'] else None
        debit_account_id = request.form['debit_account_id']
        debit_amount = Decimal(request.form['debit_amount'])
        # Credit
        credit_reference = request.form['credit_reference'].strip() if request.form['credit_reference'] else None
        credit_account_id = request.form['credit_account_id']
        credit_amount = Decimal(request.form['credit_amount'])
        
        transaction.created_at = created_at
        transaction.description = description
        transaction.installment_number = installment_number
        transaction.installment_total = installment_total
        transaction.debit_reference = debit_reference
        transaction.debit_account_id = debit_account_id
        transaction.debit_amount = debit_amount
        transaction.credit_reference = credit_reference
        transaction.credit_account_id = credit_account_id
        transaction.credit_amount = credit_amount
        transaction.is_reconciled = is_reconciled

        db.session.add(transaction)
        db.session.commit()
        return redirect(url_for('transaction_index'))

    accounts = sorted(Account.query.all(), key=lambda x: x.alias)
    created_at = pendulum.parse(str(transaction.created_at)) # type: ignore
    return render_template(
        'tables/transaction/transaction_edit.html',
        transaction=transaction,
        accounts=accounts,
        created_at_year=created_at.year, # type: ignore
        created_at_month=created_at.month, # type: ignore
        created_at_day=created_at.day, # type: ignore
        created_at_hour=created_at.hour, # type: ignore
        created_at_minute=created_at.minute, # type: ignore
    )


@app.route('/transaction/<int:transaction_id>/delete/', methods=['GET', 'POST'])
def transaction_delete(transaction_id):
    db.session.delete(Transaction.query.get_or_404(transaction_id))
    db.session.commit()
    
    return redirect(url_for('transaction_index'))
