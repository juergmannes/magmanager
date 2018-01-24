# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
    
app = Flask(__name__,static_url_path='/magmanager/static') # create the application instance
app.config.from_object(__name__) # load config from this file , magmanager.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'magmanager.db'),
    SECRET_KEY='\x0e\x15jG\xef\xed!\x81H\x03\xf0"\xcb\x86\x8f\xb2\xb3`\\l|\xcfIb'
))
app.config.from_envvar('MAGMANAGER_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv
    
def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')
    
def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
    
@app.route('/')
def home():
    db = get_db()
    cur = db.execute('select id,title from mags order by title asc')
    mags = cur.fetchall()
    cur = db.execute('select short_name from users order by short_name asc')
    users = cur.fetchall()
    return render_template('show_magazines.html', mags=mags, users=users)
    
@app.route('/add_magazine', methods=['POST'])
def add_magazine():
    db = get_db()
    # Add new magazine if it does not exist yet
    cur = db.execute('select id from mags where title = ?',[request.form['title']])
    data = cur.fetchone()
    if data is None:
        db.execute('insert into mags (title) values (?)',[request.form['title']])
        db.commit()
        flash('New magazine was successfully posted') 
    else:
        flash('Magazine already exists in database')
    return redirect(url_for('home'))

@app.route('/remove_magazine', methods=['POST'])
def remove_magazine():
    db = get_db()
    db.execute('delete from mags where id = ?',[request.form['id'],])
    db.commit()
    flash('Magazine removed')
    return redirect(url_for('home'))
    
@app.route('/magazine/<magazine_id>')
def magazine_subscribers(magazine_id):
    db = get_db()
    cur = db.execute('select title,id from mags where id = {0}'.format(magazine_id))
    mags = cur.fetchall()
    cur = db.execute('select short_name from users u join users_mags um on u.id = um.users_id where um.mags_id = {0} order by short_name'.format(magazine_id))
    users = cur.fetchall()
    return render_template('magazine_subscribers.html', mags=mags, users=users)

@app.route('/Users')
def users():
    db = get_db()
    cur = db.execute('select short_name from users order by short_name asc')
    users = cur.fetchall()
    return render_template('users.html', users=users)

@app.route('/add_user', methods=['POST'])
def add_user():
    db = get_db()
    # Add new user if it does not exist yet
    cur = db.execute('select id from users where short_name = ?',[request.form['short_name']])
    data = cur.fetchone()
    if data is None:
        db.execute('insert into users (short_name) values (?)',[request.form['short_name']])
        db.commit()
        flash('New user was successfully created') 
    else:
        flash('User already exists in database')
    return redirect(url_for('users'))
    
@app.route('/remove_user', methods=['POST'])
def remove_user():
    db = get_db()
    db.execute('delete from users where short_name = ?',[request.form['short_name'],])
    db.commit()
    flash('User removed')
    return redirect(url_for('users'))
    
@app.route('/add_subscriber', methods=['POST'])
def add_subscriber():
    db = get_db()
    # Add subscription if he/she is not a subscriber yet and he/she is an existing user
    cur = db.execute('select id from users where short_name = ?',[request.form['short_name']])
    user_record = cur.fetchone()
    cur = db.execute('select * from users_mags um join users u on um.users_id = u.id where um.mags_id = ? and u.short_name = ?',[request.form['magazine_id'],request.form['short_name']])
    data = cur.fetchone()
    if data is None and user_record is not None:
        cur = db.execute('select id from users where short_name = ?',[request.form['short_name'],])
        user_id = cur.fetchone()[0]
        db.execute('insert into users_mags (users_id,mags_id) values (?,?)',[user_id,request.form['magazine_id']])
        db.commit()
        flash('New subscriber was successfully added')
    else:
        flash('User is already a subscriber or does not exist')
    return redirect(url_for('magazine_subscribers',magazine_id=request.form['magazine_id']))

@app.route('/remove_subscriber', methods=['POST'])
def remove_subscriber():
    db = get_db()
    cur = db.execute('select id from users where short_name = ?',[request.form['short_name'],])
    user_id = cur.fetchone()[0]
    db.execute('delete from users_mags where users_id = ? and mags_id = ?',[user_id,request.form['magazine_id']])
    db.commit()
    flash('Subscription removed')
    return redirect(url_for('magazine_subscribers',magazine_id=request.form['magazine_id']))
    
@app.route('/About')
def about():
    return render_template('about.html')