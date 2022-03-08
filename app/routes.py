from flask import Flask, render_template, session, request, redirect, url_for, flash,current_app
import flask_login
from app import app
from app import oauth2
import boto3
from botocore.exceptions import ClientError
import app.dynamodb as dynamodb
from app.forms import LoginForm
import msal
import base64


with app.app_context():
    config = current_app.config
    login_manager = current_app.login_manager

@login_manager.user_loader
def load_user(user_id):
    return dynamodb.User(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))


@app.route('/',methods=['GET','POST'])
def login():
    session['facial_recognition'] = False
    session["flow"] = oauth2.ms_build_auth_code_flow(
        scopes=config['SCOPE'],
        client_id=config['CLIENT_ID'],
        client_secret=config['CLIENT_SECRET'],
        authority=config['AUTHORITY']
    ) 
    form = LoginForm(request.form)
    if form.validate_on_submit():
        if dynamodb.validate_login(Id=form.email.data,password=form.password.data):
            user = dynamodb.User(id=form.email.data)
            flask_login.login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html',title="VPN Registration",form=form,auth_url=session["flow"]["auth_uri"])

@app.route('/compare_faces', methods = ['POST'])
@flask_login.login_required
def compare_faces():
    client = boto3.client('rekognition')
    jsdata = request.form['javascript_data'][23:]
    try:
        response = client.compare_faces(
            SourceImage={
                'Bytes': base64.b64decode(jsdata)
            },
            TargetImage={
                'S3Object': {
                    'Bucket': 'facial-recognition-store',
                    'Name': f'models/{flask_login.current_user.username}.jpg',
                }
            },
            QualityFilter='NONE'
        )   
        print(response)
        if response['FaceMatches'][0]['Similarity'] >= 94:
            session['facial_recognition'] = True
            print(f'Status right after check {flask_login.current_user.facial_recognition}')
            return "Match"
        else:
            return "NoMatch"
    except (ClientError,IndexError,KeyError): # These errors are typically raised when a face isn't detected, isn't able to be processed etc
        return "NoMatch"
        
@app.route("/generate")
@flask_login.login_required
def generate():
    print(f' facial recognition status = {flask_login.current_user.facial_recognition}')
    if not flask_login.current_user.facial_recognition:
        redirect(url_for(dashboard))
    peers = ["firstPeer","secondPeer","thirdPeer","fourthPeer","fifthPeer"]
    return render_template("generate.html",peers=peers)

@app.route("/dashboard")
@flask_login.login_required
def dashboard():
    return render_template('landing.html', user=flask_login.current_user.username)


@app.route(config['REDIRECT_PATH'])  # Its absolute URL must match your app's redirect_uri set in AAD
def ms_authorized():
    try:
        cache = oauth2.ms_load_cache(session)
        result = oauth2.ms_build_msal_app(
            cache=cache,
            authority=config['AUTHORITY'],
            client_id=config['CLIENT_ID'],
            client_secret=config['CLIENT_SECRET']
            ).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        oauth2.ms_save_cache(cache=cache,session=session)
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
    try:
        dynamodb.get_user(Id=session['user']['oid'])
    except ValueError:
        dynamodb.new_user(Id=session['user']['oid'])
    user = dynamodb.User(id=session['user']['oid'])
    flask_login.login_user(user)
    return redirect(url_for('dashboard'))

@app.route("/ms-logout")
def ms_logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        config['AUTHORITY'] + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("login", _external=True))



app.jinja_env.globals.update(ms_build_auth_code_flow=oauth2.ms_build_auth_code_flow)  # Used in template
