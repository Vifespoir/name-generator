"""Flask tutorial."""

# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from french_name_generator.main import generate_name_combo
import logging

logging.basicConfig(
    level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')


# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'name_generator.db'),
    SECRET_KEY='cGtJLA6a7we46CA9Vk5abTwkjSKd8eY0hzjGs/TTet1BKx88Jzswrk+AH5jtJb\
                k3LAOP4PWGUQ+uxjIj4f25Bw==',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('NAME_GENERATOR_SETTINGS', silent=True)


def connect_db():
    """Connect to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initialize the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initialize the database."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Open a new database connection.

    Check if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def init_names():
    """Open a new database connection.

    Check if there is none yet for the
    current application context.
    """
    db = get_db()
    with app.open_resource('names.sql', mode='r') as f:
        db.cursor().executescript(f.read())
        db.commit()


@app.teardown_appcontext
def close_db(error):
    """Close the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    """Display entries from the database."""
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)


@app.route('/fr/names')
def show_names():
    """Display generated names."""
    db = get_db()
    names = []
    try:
        cur = db.execute('select firstname, lastname from query order by id desc')
        namesDB = cur.fetchall()
        for name in namesDB:
            name = (name['firstname'], name['lastname'])
            names.append(name)
    except sqlite3.OperationalError:
        names = []

    return render_template('show_names.html', names=names)


@app.route('/fr/names/generate', methods=['POST'])
def generate_names():
    """Generate French names."""
    init_names()
    logging.debug("generate_names elements posted: %s" % request.form)

    age = request.form['age'].split(' - ')
    ageL, ageH = int(age[0][:-4]), int(age[1][:-4])

    logging.debug("generate_names ages: {} - {}".format(ageL, ageH))

    try:
        request.form['lastUPPER']
        lastUPPER = True
    except Exception as e:
        logging.debug("generate_names lastUPPER error: %s" % e)
        lastUPPER = False
    logging.debug("generate_names last name upper: %s" % lastUPPER)

    if request.form['amount']:
        amount = int(request.form['amount'])
        names = generate_name_combo(amount=amount, ageL=ageL, ageH=ageH,
                                    lastUPPER=lastUPPER)

        db = get_db()
        for name in names:
            db.execute('insert into query (firstname, lastname) values (?, ?)',
                       [name[0], name[1]])
            db.commit()

        flash('New names were successfully generated')
    else:
        amount = 0
        flash('Please enter a valid amount of name to generate')

    logging.debug("generate_names amount: %s" % amount)

    return redirect(url_for('show_names'))


if __name__ == "__main__":
    app.run(host='0.0.0.0')
