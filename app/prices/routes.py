import datetime, os, requests
from flask import render_template, url_for, request
from sqlalchemy import text, func, extract, distinct
import numpy as np

import main
from app.models import Company, PriceHistory
import pandas as pd
import lxml.html as lh
from app.prices import bp
import re
from app import db, prices
from sqlalchemy.dialects.postgresql import insert

dataPath = '/content/drive/My Drive/visit.nrb@gmail.com/Python/nepse/'
# startDate = '2010-04-15'

perPage = 500

# The basic URL of NepSe
baseURL = "http://nepalstock.com/main/todays_price/index/0/?startDate={}&stock-symbol=&_limit=500"

# Get current dateTime in YYYYmmddHHMMSS for filename
dt = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
startDate = "2020-09-24"


# startDate = datetime.datetime.today().strftime('%Y-%m-%d')


@bp.route('/fetch', methods=['GET'])
def fetch_prices():
    endDate = datetime.datetime.today().strftime('%Y-%m-%d')
    dateRange = pd.date_range(startDate, endDate)

    df = pd.DataFrame()
    for singleDate in dateRange:
        thisDay = singleDate.strftime("%Y-%m-%d")
        df = loopPerDay(thisDay)
        # saveToDB(df)
        # print(df)
        # ---------- End of fetch operation
        sectors = Company.query.with_entities(Company.sector).distinct(Company.sector)
    sectors = [r for r, in sectors]
    return render_template('data_frame.html', tables=[df.to_html(classes='table-sm table table-striped ', index=False)],
                           titles=df.columns.values, sectors=sectors)


# Show the list of dates for which we have record in database
@bp.route('/records', methods=['GET'])
def fetch_dates():
    PriceQuery = db.session.query(
        PriceHistory.date,
        func.count(PriceHistory.date).label("companies_traded"),
        func.sum(PriceHistory.amount).label("total_amount"),
        func.sum(PriceHistory.no_of_txns).label("total_txns")
    ).group_by(PriceHistory.date)

    year = request.args.get('year') or "2010"
    if year is not None and int(year) > 2009:
        PriceQuery = PriceQuery.filter(extract('year', PriceHistory.date) == year)

    priceData = PriceQuery.order_by(PriceHistory.date.desc()).all()

    df = pd.DataFrame([(d.date, d.companies_traded, d.total_txns, d.total_amount) for d in priceData],
                      columns=['Date', 'Traded Companies', "No. of Txns", "Total Amount"])
    df.insert(0, '#', df.index + 1)
    df['No. of Txns'] = df['No. of Txns'].apply('{:,}'.format)
    df['Total Amount'] = df['Total Amount'].apply('{:,}'.format)

    # Extract Unique years
    # sectors = np.unique(pd.DatetimeIndex(df['Date']).year)
    sectors = db.session.query(distinct(func.date_part('YEAR', PriceHistory.date)).label("year")).all()
    # sectors = [r for r, in sectors]

    # link = url_for('main.price_history')
    df['Date'] = df['Date'].apply(anchor_link)

    # print(years)
    return render_template('prices/record_dates.html', tables=[df.to_html(classes='table-sm table table-striped ', index=False,escape=False)],
                           titles=df.columns.values, sectors=sectors)


def saveToDB(df):
    df = df[10:]
    print(df)
    # print(df.columns.values)
    for index, row in df.iterrows():
        # print(row)
        # priceHistory = PriceHistory(
        #     date=row['Date'],
        #     company=row['Company'],
        #     no_of_txns=row['No. Of Txns'],
        #     max_price=row['Max Price'],
        #     min_price=row['Min Price'],
        #     closing_price=row['Closing Price'],
        #     traded_shares=row['Traded Shares'],
        #     amount=row['Amount'],
        #     previous_closing=row['Previous Closing'],
        #     difference=row['Difference Rs.'],
        # )
        # db.session.add(priceHistory)
        # db.session.commit()
        # pass
        stmt = insert(PriceHistory.__table__).values(date=row['Date'],
                                                     company=row['Company'],
                                                     no_of_txns=row['No. Of Txns'],
                                                     max_price=row['Max Price'],
                                                     min_price=row['Min Price'],
                                                     closing_price=row['Closing Price'],
                                                     traded_shares=row['Traded Shares'],
                                                     amount=row['Amount'],
                                                     previous_closing=row['Previous Closing'],
                                                     difference=row['Difference Rs.'])
        stmt = stmt.on_conflict_do_nothing()
        conn = db.session.get_bind().connect()
        # print(conn.type())
        conn.execute(stmt)


def loopPerDay(thisDate):
    # Loop infinitely till the nepse URL Is fetched
    # while True:
    #   try:
    tr_elements = fetchPageData(thisDate)
    #   break
    # except Exception: # Replace Exception with something more specific.
    # print("Failed!! Retryting...")
    # continue

    # -------- Process and save first page data
    df = processPageAndSave(tr_elements, "All", thisDate)

    # ----------- Last Row includes number of txns
    tr_txns_count = tr_elements[-1]
    txnSummarySave(tr_txns_count, thisDate)

    # ----------- Total Quantity Row
    tr_txns_qty = tr_elements[-2]
    txnSummarySave(tr_txns_qty, thisDate)

    # ----------- Total Amount Row
    tr_txns_amt = tr_elements[-3]
    txnSummarySave(tr_txns_amt, thisDate)

    return df


def txnSummarySave(T, thisDate):
    col = [('Title', []), ('Value', [])]
    i = 0
    for t in T.iterchildren():
        data = t.text_content()
        # Check if row is empty
        if i > 0:
            # Convert any numerical value to integers
            try:
                data = int(data)
            except:
                pass

        # Append the data to the empty list of the i'th column
        col[i][1].append(data)
        # Increment i for the next column

        i += 1

    Dict = {title: column for (title, column) in col}
    df = pd.DataFrame(Dict)

    # Insert Date in Data
    df.insert(1, 'Date', thisDate)
    # print(df)
    # Save the dataframe to brand new csv file
    fullFileName = dataPath + "nepse_TxnSummary_" + (startDate.replace('-', "")) + "_" + dt + ".csv"
    # df.to_csv(fullFileName, mode='a', header=not os.path.isfile(fullFileName), index=False)
    return df


def processPageAndSave(tr_elements, fileName, thisDate):
    # Since we know in advance he column names lets put them here
    col = [('S.N.', []),
           ('Company', []),
           ('No. Of Txns', []),
           ('Max Price', []),
           ('Min Price', []),
           ('Closing Price', []),
           ('Traded Shares', []),
           ('Amount', []),
           ('Previous Closing', []),
           ('Difference Rs.', [])]

    for j in range(2, len(tr_elements)):
        # T is our j'th row
        T = tr_elements[j]
        # If row is not of size 10, the //tr data is not from our table
        if len(T) != 10:
            continue
        # i is the index of our column
        i = 0
        # Iterate through each element of the row
        for t in T.iterchildren():
            data = t.text_content()
            # Check if row is empty
            if i > 0:
                try:
                    # Remove New line character
                    data = re.sub("[^a-zA-Z0-9-%/ ()^.]", "", data)
                    # data = re.sub(r'[^\x00-\x7F]+', ' ', data)

                    # data = re.sub("\\n", "", data)
                except:
                    print("failed")

                    pass

            # Append the data to the empty list of the i'th column
            col[i][1].append(data)
            # Increment i for the next column

            i += 1
    Dict = {title: column for (title, column) in col}
    df = pd.DataFrame(Dict)

    # Insert Date in Data
    df.insert(1, 'Date', thisDate)
    # print(df)
    # Save the dataframe to brand new csv file
    fullFileName = dataPath + fileName + "_priceHistory_" + (startDate.replace('-', "")) + "_" + dt + ".csv"
    # df.to_csv(fullFileName, mode='a', header=not os.path.isfile(fullFileName), index=False)
    return df


def fetchPageData(thisDate):
    currentURL = baseURL.format(thisDate)
    # print(currentURL)

    # Create a handle, page, to handle the contents of the website
    page = requests.get(currentURL)

    # Store the contents of the website under doc
    doc = lh.fromstring(page.content)
    # print(doc)

    # Parse data that are stored between <tr>..</tr> of HTML
    tr_elements = doc.xpath('//tr')

    return tr_elements


def anchor_link(val):
    return '<a target="_blank" href="/prices?day={0}">{0}</a>'.format(val)
