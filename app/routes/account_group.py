from models import db, AccountGroup
from flask import render_template, request, url_for, redirect
from app_build import app


def get_available_account_groups(account_group_id: int | None = None) -> list[AccountGroup]:
    def get_recursive_account_group_ids(account_group_id: int) -> list[int]:
        account_group_ids = [account_group_id]
        for child_account_group in AccountGroup.query.filter(AccountGroup.parent_account_group_id == account_group_id).all():
            account_group_ids += get_recursive_account_group_ids(child_account_group.id)
        return account_group_ids

    if account_group_id is None:
        return sorted(AccountGroup.query.all(), key=lambda x: x.alias.lower())

    descendant_account_group_ids = get_recursive_account_group_ids(account_group_id)
    return sorted(AccountGroup.query.filter(AccountGroup.id.notin_(descendant_account_group_ids)).all(), key=lambda x: x.alias.lower())


@app.route('/account_group/')
def account_group_index():
    alert_message = request.args.get('alert_message')
    account_groups = AccountGroup.query.order_by(AccountGroup.name).all()
    return render_template(
        'tables/account_group/account_group_index.html',
        account_groups=account_groups,
        alert_message=alert_message
    )


@app.route('/account_group/create/', methods=['GET', 'POST'])
def account_group_create():
    
    account_groups=sorted(AccountGroup.query.all(), key=lambda x: x.alias.lower())
    
    if request.method == 'POST':
        
        name = request.form['name']
        description = request.form['description'] if request.form['description'] else None
        parent_account_group_id = request.form['parent_account_group_id'] if request.form['parent_account_group_id'] else None

        db.session.add(AccountGroup(
            name=name,
            description=description,
            parent_account_group_id=parent_account_group_id
        ))
        db.session.commit()
        return redirect(url_for('account_group_index'))

    return render_template(
        'tables/account_group/account_group_create.html',
        account_groups=account_groups
    )


@app.route('/account_group/<int:account_group_id>/edit/', methods=['GET', 'POST'])
def account_group_edit(account_group_id):
    
    available_account_groups = get_available_account_groups(account_group_id=account_group_id)
    account_group = AccountGroup.query.get_or_404(account_group_id)

    if request.method == 'POST':
        
        name = request.form['name']
        description = request.form['description'] if request.form['description'] else None
        parent_account_group_id = request.form['parent_account_group_id'] if request.form['parent_account_group_id'] else None
            
        account_group.name = name
        account_group.description = description
        account_group.parent_account_group_id = parent_account_group_id

        db.session.add(account_group)
        db.session.commit()
        return redirect(url_for('account_group_index'))
    
    return render_template(
        'tables/account_group/account_group_edit.html',
        account_group=account_group,
        available_account_groups=available_account_groups,
    )


@app.route('/account_group/<int:account_group_id>/delete/', methods=['GET', 'POST'])
def account_group_delete(account_group_id):
    if AccountGroup.query.filter(AccountGroup.parent_account_group_id == account_group_id).all():
        message = f"Cannot delete account group (id: {account_group_id}) with children."
        return redirect(url_for('account_group_index', alert_message=message))
    
    if AccountGroup.query.filter(AccountGroup.id == account_group_id).first().accounts:
        message = f"Cannot delete account group (id: {account_group_id}) with accounts."
        return redirect(url_for('account_group_index', alert_message=message))
    
    db.session.delete(AccountGroup.query.get_or_404(account_group_id))
    db.session.commit()
    
    return redirect(url_for('account_group_index'))
