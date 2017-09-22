from flask import Flask, render_template, request, redirect, url_for,flash,jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base,User,Food
app = Flask(__name__)
from flask import session as login_session
import random,string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
engine = create_engine('postgresql://food:kunal@localhost/food')
#engine = create_engine('sqlite:///food.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
CLIENT_ID = json.loads(open('/var/www/client_secrets.json', 'r').read(
))['web']['client_id']

@app.route('/foods/JSON')
def foodJSON():
    food=session.query(Food).all()
    if login_session.has_key('email') and login_session['email']:
         return jsonify(FoodItems=[i.serialize for i in food])
    return redirect(url_for('showall'))

def createState():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return

@app.route('/foods/<string:categories>',methods=['GET','POST'])
def sort(categories):
    cat=session.query(Food).filter_by(categories=categories)
    return render_template('main.html',food=cat)

@app.route('/gconnect', methods=['GET','POST'])
def gconnect():
    # Validate state token
    if not login_session.has_key('state'):
        createState();
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    print login_session['credentials']
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    user_info=session.query(User).filter_by(email=login_session['email']).first()
    if user_info is None:
        User(name=login_session['username'],email=login_session['email'],picture=login_session['picture'])
    return jsonify(
        name=login_session['username'],
        email=login_session['email'],
        img=login_session['picture']
    )


@app.route('/gdisconnect')
def gdisconnect():
    credentials=login_session['credentials']
    access_token = credentials.access_token
    print access_token
    if access_token is None:
        print "you are not logged in"
    else:
        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % access_token
        header = httplib2.Http()
        result = header.request(url, 'GET')[0]
        print result['status']
        if result['status']=='200':
           del login_session['credentials']
           del login_session['username']
           del login_session['picture']
           del login_session['email']
           print "Successfully logged out"
        else:
           print "error disconnecting"
    return redirect(url_for('showall'))

@app.route('/')
@app.route('/foods',methods=['GET','POST'])
def showall():
      createState()
      food=session.query(Food).all()
      if login_session.has_key('email') and login_session['email']:
          print "sada";
          flag = 1
          return render_template('main.html',food=food,STATE = login_session['state'],flag = flag,name=login_session['username'],image=login_session['picture'])
      flag = 0
      if login_session.has_key('email') and login_session['email']:
          flag = 1
          return render_template('main.html',food=food,STATE = login_session['state'],flag = flag,name=login_session['username'],image=login_session['picture'])
      return render_template('main.html',food=food,STATE = login_session['state'],flag = flag,name='',image='')

@app.route('/foods/new',methods=['POST'])
def addNewfood():
      if request.method == 'POST':
          newItem = Food(name=request.form['name'],description=request.form['desc'],image=request.form['img'],categories=request.form['cat'])
          print newItem
          session.add(newItem)
          session.commit()
          return redirect(url_for('showall'))


@app.route('/foods/edit/<int:foodid>/',methods=['POST'])
def edit(foodid):
    itemtoedit=session.query(Food).filter_by(id=foodid).first()
    if request.method=='POST':
         name=request.form['name']
         description=request.form['desc']
         image=request.form['img']
         categories=request.form['cat']
         if not name=="":
            itemtoedit.name=name
         if not description=="":
            itemtoedit.description=description
         if not image=="":
            itemtoedit.image=image
         if not categories=="":
            itemtoedit.categories=categories
         session.add(itemtoedit)
         session.commit()
         return redirect(url_for('showall'))

@app.route('/foods/delete/<int:foodid>/')
def delete(foodid):
    delete = session.query(Food).filter_by(id=foodid).first()
    session.delete(delete)
    session.commit()
    return redirect(url_for('showall'))

if __name__ == '__main__':
    app.secret_key='super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
