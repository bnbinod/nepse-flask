from flask import render_template, request, current_app
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from app import db

from app.models import Company, PriceHistory
import pandas as pd
from flask_login import current_user, login_required
from flask_paginate import Pagination
from app.main import bp


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    if current_user.is_authenticated:
        status = "User logged in."
    else:
        status = "User not logged in."
    # return render_template('emails.html', email_addresses=email_addresses)
    author = "Page Title"
    name = "Author Name"
    data = {"var1": author, "var2": name, "status": status}
    return render_template('index.html', data=data)


@bp.route('/companies', methods=['GET'])
@login_required
def companies():
    # df = Company.query.all()
    page = request.args.get('page', 1, type=int)

    CompanyQuery = Company.query

    currentSector = request.args.get('sector', None, type=str)
    if currentSector is not None and len(currentSector) > 2:
        CompanyQuery = CompanyQuery.filter(Company.sector == currentSector)

    searchTerm = request.args.get('term', None, type=str)
    if searchTerm is not None and len(searchTerm) > 0:
        search = "%{}%".format(searchTerm)
        CompanyQuery = CompanyQuery.filter(
            or_(Company.name.ilike(search), Company.sector.ilike(search), Company.scrip.ilike(search)))

    list_companies = CompanyQuery.paginate(page, current_app.config['ITEMS_PER_PAGE'], False)
    pagination = Pagination(page=page, per_page=current_app.config['ITEMS_PER_PAGE'], total=CompanyQuery.count(), bs_version=4,
                            record_name='companies')

    # Get Unique Sectors for dropdown
    sectors = Company.query.with_entities(Company.sector).distinct(Company.sector)
    sectors = [r for r, in sectors]

    return render_template('companies.html', sectors=sectors, companies=list_companies.items, pagination=pagination)


@bp.route('/prices', methods=['GET'])
@login_required
def price_history():
    # page = request.args.get('page', 1, type=int)

    PriceQuery = PriceHistory.query.options(joinedload('company_model'))

    # currentSector = request.args.get('sector', None, type=str)
    # if currentSector is not None and len(currentSector) > 2:
    #     PriceQuery = PriceQuery.filter(
    #         PriceHistory.company_model is not None and PriceHistory.company_model.sector == currentSector)

    priceData = PriceQuery.order_by(PriceHistory.date.desc()).limit(
        100).all()

    # list_companies = CompanyQuery.paginate(page, app.config['ITEMS_PER_PAGE'], False)
    # pagination = Pagination(page=page, per_page=app.config['ITEMS_PER_PAGE'], total=CompanyQuery.count(), bs_version=4,
    #                         record_name='companies')

    # Get Unique Sectors for dropdown
    sectors = Company.query.with_entities(Company.sector).distinct(Company.sector)
    sectors = [r for r, in sectors]

    df = pd.DataFrame([(d.id, d.date, d.company, d.no_of_txns, d.max_price, d.min_price, d.closing_price,
                        d.traded_shares, d.amount, d.previous_closing, d.difference,
                        d.company_model.sector if d.company_model is not None else "") for d in priceData],
                      columns=['#', 'Date', 'Company', "No. of Txns", "Max", "Min", "Closing", "Traded Shares",
                               "Amount", "Pre. Closing", "Difference", "Sector"])
    return render_template('data_frame.html', tables=[df.to_html(classes='table-sm table table-striped ', index=False)],
                           titles=df.columns.values, sectors=sectors)


@bp.route('/tables', methods=['GET'])
def tables():
    df = db.engine.table_names()
    print(df)
    return render_template('companies.html', tables=[df.to_html(classes='table table-striped', index=False)],
                           titles=df.columns.values)
