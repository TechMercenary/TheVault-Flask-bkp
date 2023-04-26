from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import TypeDecorator, Integer
import pendulum
import datetime


db = SQLAlchemy()


def get_account_total_by_transaction_group(transaction_group, account):

    total = 0 
    for transaction in transaction_group.transactions:
        if transaction.debit_account_id == account.id:
            if account.side == 'DEBIT':
                total += transaction.debit_amount
            else:
                total -= transaction.debit_amount
        elif transaction.credit_account_id == account.id:
            if account.side == 'CREDIT':
                total += transaction.credit_amount
            else:
                total -= transaction.credit_amount

    return total


# TODO: Review the need for to_dict() method
class BaseModel(db.Model):
    __abstract__ = True

    def to_dict(self):
        data = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime.date):
                value = value.strftime('%Y-%m-%d')
            # if isinstance(value, datetime.date):
            #     value = pendulum.instance(datetime.datetime.combine(value, datetime.time.min))
            #     value = value.to_datetime_string()
            #     # value = pendulum.instance(value).to_iso8601_string(extended=True)
            column_type = str(column.type)
            data[column.name] = {
                'value': value,
                'type': column_type
            }
        return data


class Currency(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Text, unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    

class AccountGroup(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    parent_account_group_id = db.Column(db.Integer, db.ForeignKey('account_group.id'), nullable=True)

    parent_account_group = db.relationship('AccountGroup', remote_side=[id], foreign_keys=[parent_account_group_id], backref=db.backref('children_groups'))

    @property
    def alias(self):
        if self.parent_account_group:
            return f"{self.parent_account_group.alias} > {self.name}"
        else:
            return self.name

    @property
    def accounts(self):
        return sorted(
            Account.query.filter_by(account_group_id=self.id).all(),
            key=lambda account: account.alias
        )
        

class AccountType(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    normal_side = db.Column(db.Text, nullable=False)


class Account(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    number = db.Column(db.Text, nullable=True)
    currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'), nullable=False)
    opened_at = db.Column(db.DateTime(timezone=True), nullable=False)
    closed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    account_group_id = db.Column(db.Integer, db.ForeignKey('account_group.id'), nullable=False)
    account_type_id = db.Column(db.Integer, db.ForeignKey('account_type.id'), nullable=False)
    
    currency = db.relationship('Currency', foreign_keys=[currency_id])
    account_group = db.relationship('AccountGroup', foreign_keys=[account_group_id])
    account_type = db.relationship('AccountType', foreign_keys=[account_type_id])

    @property
    def alias(self):
        return f"{self.account_group.alias} > {self.name} [{self.account_type.name}]"

    @property
    def overdrafts(self):
        return AccountOverdraft.query.filter_by(account_id=self.id).order_by(AccountOverdraft.started_at.desc()).all()


class AccountOverdraft(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    started_at = db.Column(db.DateTime(timezone=True), nullable=False)
    limit_amount = db.Column(db.Numeric(18,2), nullable=True)
    
    account = db.relationship('Account', foreign_keys=[account_id])
    

class Transaction(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    description = db.Column(db.Text, nullable=False, default='')
    installment_number = db.Column(db.Integer, nullable=True)
    installment_total = db.Column(db.Integer, nullable=True)
    debit_reference = db.Column(db.Text, nullable=True, default='')
    debit_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    debit_amount = db.Column(db.Numeric(18,2), nullable=False)
    credit_reference = db.Column(db.Text, nullable=True, default='')
    credit_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    credit_amount = db.Column(db.Numeric(18,2), nullable=False)
    is_reconciled = db.Column(db.Boolean, nullable=False, default=False)

    debit_account = db.relationship('Account', foreign_keys=[debit_account_id])
    credit_account = db.relationship('Account', foreign_keys=[credit_account_id])



class CreditCard(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    cash_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    issuer = db.Column(db.Text, nullable=False)
    number = db.Column(db.Text, nullable=False)
    started_at = db.Column(db.DateTime(timezone=True), nullable=False)
    ended_at = db.Column(db.DateTime(timezone=True), nullable=True)
    expiration_year = db.Column(db.Integer, nullable=False)
    expiration_month = db.Column(db.Integer, nullable=False)
    
    cash_account = db.relationship('Account', foreign_keys=[cash_account_id], backref=db.backref('creditcards'))
    cc_account = db.relationship('Account', foreign_keys=[account_id])


# class CreditCardSummary(BaseModel):
#     id = db.Column(db.Integer, primary_key=True)
#     credit_card_id = db.Column(db.Integer, db.ForeignKey('credit_card.id'), nullable=False)
#     opening_date = db.Column(db.Date, nullable=False)
#     closing_date = db.Column(db.Date, nullable=False)
#     due_date = db.Column(db.Date, nullable=False)
#     next_opening_date = db.Column(db.Date, nullable=False)
#     next_closing_date = db.Column(db.Date, nullable=False)
#     next_due_date = db.Column(db.Date, nullable=False)
#     tasa_nominal_anual = db.Column(db.Numeric(18,2), nullable=False, default=0)
#     tasa_efectiva_mensual = db.Column(db.Numeric(18,2), nullable=False, default=0)
#     limit_purchase = db.Column(db.Numeric(18,2), nullable=False, default=0)
#     limit_installment = db.Column(db.Numeric(18,2), nullable=False, default=0)
#     limit_financing = db.Column(db.Numeric(18,2), nullable=False, default=0)
#     limit_advance = db.Column(db.Numeric(18,2), nullable=False, default=0)
    
#     credit_card = db.relationship('CreditCard', foreign_keys=[credit_card_id], backref=db.backref('summaries'))


# class CreditCardSummaryBalance(BaseModel):
#     id = db.Column(db.Integer, primary_key=True)
#     credit_card_summary_id = db.Column(db.Integer, db.ForeignKey('credit_card_summary.id'), nullable=False)
#     currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'), nullable=False)
#     amount = db.Column(db.Numeric(18,2), nullable=False)
    
#     __table_args__ = (db.UniqueConstraint('credit_card_summary_id', 'currency_id'),)
    
#     credit_card_summary = db.relationship('CreditCardSummary', foreign_keys=[credit_card_summary_id], backref=db.backref('balances'))
#     currency = db.relationship('Currency', foreign_keys=[currency_id])

    
# class CreditCardSummaryTransaction(BaseModel):
#     id = db.Column(db.Integer, primary_key=True)
#     credit_card_summary_id = db.Column(db.Integer, db.ForeignKey('credit_card_summary.id'), nullable=False)
#     transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    
#     credit_card_summary = db.relationship('CreditCardSummary', foreign_keys=[credit_card_summary_id], backref=db.backref('summary_transactions'))
#     transaction = db.relationship('Transaction', foreign_keys=[transaction_id])


# class Employer(BaseModel):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.Text, unique=True, nullable=False)
#     started_at = db.Column(db.DateTime(timezone=True), nullable=False)
#     ended_at = db.Column(db.DateTime(timezone=True), nullable=True)
#     cash_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
#     salary_revenue_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
#     salary_receivable_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
#     salary_deferred_revenue_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
#     salary_tax_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
#     salary_expense_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    
#     cash_account = db.relationship('Account', foreign_keys=[cash_account_id])
#     salary_revenue_account = db.relationship('Account', foreign_keys=[salary_revenue_account_id])
#     salary_receivable_account = db.relationship('Account', foreign_keys=[salary_receivable_account_id])
#     salary_deferred_revenue_account = db.relationship('Account', foreign_keys=[salary_deferred_revenue_account_id])
#     salary_tax_account = db.relationship('Account', foreign_keys=[salary_tax_account_id])
#     salary_expense_account = db.relationship('Account', foreign_keys=[salary_expense_account_id])




# class Salary(BaseModel):
#     id = db.Column(db.Integer, primary_key=True)
#     transaction_group_id = db.Column(db.Integer, db.ForeignKey('transaction_group.id'), nullable=False)
#     employer_id = db.Column(db.Integer, db.ForeignKey('employer.id'), nullable=False)
#     period = db.Column(db.Text, nullable=False)
#     description = db.Column(db.Text, nullable=False, default='')
    
#     employer = db.relationship('Employer', foreign_keys=[employer_id], backref=db.backref('salaries'))
#     transaction_group = db.relationship('TransactionGroup', foreign_keys=[transaction_group_id], backref=db.backref('salary', uselist=False))

#     @property
#     def total_revenue(self):
#         return get_account_total_by_transaction_group(
#             transaction_group=self.transaction_group,
#             account=self.employer.salary_revenue_account
#         )
 
#     @property
#     def total_deferred_revenue(self):
        
#         return get_account_total_by_transaction_group(
#             transaction_group=self.transaction_group,
#             account=self.employer.salary_deferred_revenue_account
#         )
    
#     @property
#     def total_tax(self):
        
#         return get_account_total_by_transaction_group(
#             transaction_group=self.transaction_group,
#             account=self.employer.salary_tax_account
#         )

#     @property
#     def total_expense(self):
        
#         return get_account_total_by_transaction_group(
#             transaction_group=self.transaction_group,
#             account=self.employer.salary_expense_account
#         )

#     @property
#     def total_cash(self):
        
#         return get_account_total_by_transaction_group(
#             transaction_group=self.transaction_group,
#             account=self.employer.cash_account
#         )
