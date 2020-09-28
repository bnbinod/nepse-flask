from flask import Flask, render_template
from flask import request, redirect
from flask import session
from flask import g
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import pandas as pd

app = Flask(__name__)
email_addresses = []
app.secret_key = '#d\xe9X\x00\xbe~Uq\xebX\xae\x81\x1fs\t\xb4\x99\xa3\x87\xe6.\xd1_'


# Database Connection
# ----------------- Connect eTB WareHouse
def connect_db():
    # Postgres username, password, and database name
    POSTGRES_ADDRESS = '202.45.146.72'  ## INSERT YOUR DB ADDRESS IF IT'S NOT ON PANOPLY
    POSTGRES_PORT = '8995'
    POSTGRES_USERNAME = 'warehouse'  ## CHANGE THIS TO YOUR PANOPLY/POSTGRES USERNAME
    POSTGRES_PASSWORD = 'Qw23@E#R'  ## CHANGE THIS TO YOUR PANOPLY/POSTGRES PASSWORD
    POSTGRES_DBNAME = 'history'  ## CHANGE THIS TO YOUR DATABASE NAME
    # A long string that contains the necessary Postgres login information
    postgres_str = ("postgresql://{username}:{password}@{ipaddress}:{port}/{dbname}".format(username=POSTGRES_USERNAME,
                                                                                            password=POSTGRES_PASSWORD,
                                                                                            ipaddress=POSTGRES_ADDRESS,
                                                                                            port=POSTGRES_PORT,
                                                                                            dbname=POSTGRES_DBNAME))

    # Create the connection
    cnx = create_engine(postgres_str)
    return cnx


@app.route('/db')
def read_database():
    cnx = connect_db()
    # column_names = ["id", 'date', 'contract_number', 'symbol', 'buyer', 'seller', 'quantity', 'rate', 'amount']
    # df = pd.DataFrame(columns=column_names)
    db = scoped_session(sessionmaker(bind=cnx))
    dbEx = db.execute("SELECT * FROM price_history limit 10")
    df = pd.DataFrame(dbEx.fetchall())
    df.columns = dbEx.keys()

    # df = cnx.table_names()
    print(df)
    # data = df
    data = {"var1": "VAR-1", "var2": "name", "emails": email_addresses}
    # df.index.name = 'id'
    # del df['index']
    return render_template('nepse_companies.html', data=data,
                           tables=[df.to_html(classes='table table-striped', index=False)],
                           titles=df.columns.values)


@app.route('/')
def hello_world():
    email_addresses = g.db.execute("SELECT email FROM email_addresses").fetchall()
    # return render_template('emails.html', email_addresses=email_addresses)
    author = "Page Title"
    name = "Author Name"
    data = {"var1": author, "var2": name, "emails": email_addresses}
    return render_template('index.html', data=data)


@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['email']
    # email_addresses.append(email)
    g.db.execute("INSERT INTO email_addresses VALUES (?)", [email])
    g.db.commit()

    # print(email_addresses)
    session['email'] = email
    return redirect('/')


@app.route('/unregister')
def unregister():
    # Make sure they've already registered an email address
    if 'email' not in session:
        return "You haven't submitted an email!"
    email = session['email']
    # Make sure it was already in our address list
    if email not in email_addresses:
        return "That address isn't on our list"
    email_addresses.remove(email)
    del session['email']  # Make sure to remove it from the session
    return 'We have removed ' + email + ' from the list!'


@app.before_request
def before_request():
    g.db = sqlite3.connect("emails.db")


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


if __name__ == '__main__':
    app.run(debug=True)
