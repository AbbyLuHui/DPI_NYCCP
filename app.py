#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy import exc
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, flash, abort
from dotenv import load_dotenv
import datetime
from collaborative_filtering import cofi

#load_dotenv()

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@104.196.18.7/w4111
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.18.7/w4111"
#
DATABASEURI = "mysql+pymysql://dpi:dpi@129.236.209.131/dpifall2019"
#

#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    pass
    g.conn = engine.connect();
  except:
    print ("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    pass
    g.conn.close()
  except Exception as e:
    pass

#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
def get_rec(eventlist, user):
    return cofi(eventlist, user)

events = [
    {'eid': '1', 'name': "Meal Grabbing", 'location': "lerner", 'time':"1 am", 'category': "Food", 'description': "Trying out new restaurants"},
    {'eid': '2', 'name': "Central Park Run", 'location': "lerner", 'time':"1 am", 'category': "Exercise", 'description': "Running in Central Park"},
    {'eid': '3', 'name': "Aerospace Info Session", 'location': "lerner", 'time':"1 am", 'category': "Academic", 'description': "Info session for aerospace engineering majors"},
  ]
numppl = 40

@app.route('/event/<eid>')
def eventrender(eid):
  events = next(g.conn.execute(text("select * from event where eid = :eid"), eid=eid))
  return render_template("event.html", events = events, numppl = numppl)

@app.route('/allevent')
def alleventrender():
  events = list(g.conn.execute(text("select * from event")))
  event_proxy = []

  for i in range(len(events)):
      diff = events[i]['time'] - datetime.datetime.now()
      event_proxy.append(dict(events[i].items()))
      event_proxy[i]['days'] = diff.days
      event_proxy[i]['hours'] = diff.seconds // 3600

  return render_template("allevent.html", events = event_proxy, numppl = numppl)

@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """
  #return render_template("index.html", events=events)
  if not session.get('logged_in'):
      return render_template('login.html')
  else:
      # events = vanilla(list(g.conn.execute("select * from event where event.time > now()")))
      events = list(g.conn.execute(text("select eid from event e where not exists (select * from rsvp r where " +
                                                "r.eid = e.eid and r.uid = :uid) and not exists (select * from reject r2 where r2.eid = e.eid and r2.uid = :uid);"),
                                                uid = int(session['uid'])))

      event_ids = get_rec([sub['eid'] for sub in events],int(session['uid']))
      print("========================" + str(len(events)))
      event_proxy = []

      for i in range(4):
          if (i < len(event_ids)):
              event = next(g.conn.execute(text("select * from event where eid=:eid"), eid=event_ids[i]))
              diff = event['time'] - datetime.datetime.now()
              event_proxy.append(dict(event.items()))
              event_proxy[i]['days'] = diff.days
              event_proxy[i]['hours'] = diff.seconds // 3600

      user = next(g.conn.execute(text('select * from user where uid = :uid'), uid=session['uid']))
      return render_template("index.html", headline=event_proxy[0], events=event_proxy[1:], user=user)

  # DEBUG: this is debugging code to see what request looks like
  # print request.args

  #
  # example of a database query
  #
  # cursor = g.conn.execute("SELECT name FROM test")
  # names = []
  # for result in cursor:
  #   names.append(result['name'])  # can also be accessed using result[0]
  # cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #
  #     # creates a <div> tag for each element in data
  #     # will print:
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  # context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #


@app.route('/login', methods=['POST'])
def do_login():
    account = request.form['account']
    password = request.form['password']

    try:
        result = list(g.conn.execute(text('select uid from authentication where account = :account and password = :password'),
                        account=account, password=password))
    except exc.SQLAlchemyError as err:
        return render_template('error.html', msg = str(err.__dict__['orig']))

    if (len(result) == 0):
        flash('wrong password!')
        return index()

    session['logged_in'] = True
    session['uid'] = int(result[0]['uid'])

    return redirect('/')

# def do_admin_login():
#     if request.form['password'] == 'password' and request.form['username'] == 'admin':
#         session['logged_in'] = True
#         return redirect('/')
#     else:
#         flash('wrong password!')
#     return index()

@app.route('/signup', methods = ['GET'])
def signup():
    return render_template("signup.html")

@app.route('/signup-post', methods = ['POST'])
def do_signup():
    account = request.form['account']
    password = request.form['password']

    if (account == '' or password == ''):
        flash("account / password cannot be null!")
        return redirect('/signup')

    try:
        g.conn.execute(text('insert into authentication(account, password) values (:account, :password)'),
                        account=account, password=password)
    except exc.SQLAlchemyError as err:
        return render_template('error.html', msg = str(err.__dict__['orig']))

    uid = g.conn.execute(text('select uid from authentication where account = :account'), account=account).fetchone()['uid']
    session['uid'] = int(uid)
    session['logged_in'] = True

    return redirect('/survey/' + str(uid))

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return index()

@app.route('/survey/<uid>')
def survey(uid):
  return render_template("survey.html", uid=uid)

@app.route('/survey-add', methods=['POST'])
def survey_add():
  social = request.form['social']
  professional = request.form['professional']
  relaxing = request.form['relaxing']
  educational = request.form['educational']
  athletic = request.form['athletic']

  first_name = request.form['first-name']
  last_name = request.form['last-name']
  uni = request.form['uni']
  major = request.form['major']
  year = request.form['year']
  bio = request.form['bio']

  uid = request.form['uid']
  account = next(g.conn.execute(text('select account from authentication where uid = :uid'), uid=int(uid)))['account']

  try:
      g.conn.execute(text("insert into user(uid, first_name, last_name, uni, major, year, contact, bio, social, professional, relaxing, educational, athletic) \
                        values(:uid, :first_name, :last_name, :uni, :major, :year, :contact, :bio, :social, :professional, :relaxing, :educational, :athletic)"),
                        uid = int(uid), first_name=first_name, last_name=last_name, uni = uni, major = major, year = year, contact = account, bio = bio, social = social, educational = educational,
                        relaxing = relaxing, professional = professional, athletic = athletic)
  except exc.SQLAlchemyError as err:
      return render_template('error.html', msg = str(err.__dict__['orig']))


  return redirect('/')

@app.route('/event-creation')
def event_creation():
  return render_template("event_creation.html")

@app.route('/event-creation-add', methods=['POST'])
def event_creation_add():
  #Insert data into table
  return redirect('/')

@app.route('/rsvp-post/<int:eid>', methods = ['POST'])
def rsvp(eid):

    if ('logged_in' not in session or session['logged_in'] == False):
        redirect('/')

    try:
        g.conn.execute(text('insert into rsvp (uid, eid) values (:uid, :eid)'), uid=session['uid'], eid=eid)
    except exc.SQLAlchemyError as err:
        print("=======================" + str(session['uid']))
        print("=======================" + str(err.__dict__['orig']))
        # return render_template('error.html', msg = str(err.__dict__['orig']))
    return redirect('/')

@app.route('/reject-post/<int:eid>', methods = ['POST'])
def reject(eid):
    try:
        g.conn.execute(text('insert into reject (uid, eid) values (:uid, :eid)'), uid=session['uid'], eid=eid)
    except exc.SQLAlchemyError as err:
        print("=======================" + str(session['uid']))
        print("=======================" + str(err.__dict__['orig']))
        # return render_template('error.html', msg = str(err.__dict__['orig']))
    return redirect('/')

@app.route('/profile/<int:uid>')
def profile(uid):
    try:
        user = next(g.conn.execute(text('select * from user where uid = :uid'), uid=uid))
        created = list(g.conn.execute(text('select * from event where starter = :uid'), uid=uid))
        rsvped = list(g.conn.execute(text('select * from event e join rsvp r where r.eid = e.eid and r.uid = :uid'), uid=uid))
    except exc.SQLAlchemyError as err:
        print("=======================" + str(err.__dict__['orig']))
        # return render_template('error.html', msg = str(err.__dict__['orig']))

    return render_template("profile.html", user=user, created=created, rsvped=rsvped)

@app.route('/create-event')
def create_event():
    if ('logged_in' not in session or session['logged_in'] == False):
        return redirect('/')

    return render_template("event_creation.html")

@app.route('/create-event-add', methods=['POST'])
def create_event_add():
    name = request.form['name']
    location = request.form['location']
    category = request.form['category']
    description = request.form['description']
    time = request.form['time']
    date = request.form['date']

    datetime = date + " " + time + ":00"

    social = request.form['social']
    professional = request.form['professional']
    relaxing = request.form['relaxing']
    educational = request.form['educational']
    athletic = request.form['athletic']

    uid = session['uid']

    try:
        g.conn.execute(text('insert into event (name, location, category, description, time, starter, social, professional, educational, relaxing, athletic) values'
                            + '(:name, :location, :category, :description, :time, :starter, :social, :professional, :educational, :relaxing, :athletic)'),
                            name=name, location=location, category=category, description=description, time=datetime, starter=uid, social=float(social),
                            professional=float(professional), educational=float(educational), relaxing=float(relaxing), athletic=float(athletic))
        eid = int(next(g.conn.execute(text('select * from event where name=:name, location=:location'), name=name, location=location))['eid'])
        g.conn.execute(text('insert into create (uid, eid) values (:uid, :eid)'), uid=uid, eid=eid)
    except exc.SQLAlchemyError as err:
        print("=======================" + str(err.__dict__['orig']))
        # return render_template('error.html', msg = str(err.__dict__['orig']))

    return redirect('/')

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print ("running on %s:%d" % (HOST, PORT))
    app.secret_key = os.urandom(12)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
