from flask import Flask, render_template, session, request, redirect, url_for, flash,current_app
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

@app.route('/',methods=['GET','POST'])
def login():
    session["flow"] = oauth2.ms_build_auth_code_flow(
        scopes=config['SCOPE'],
        client_id=config['CLIENT_ID'],
        client_secret=config['CLIENT_SECRET'],
        authority=config['AUTHORITY']
        )
    
    form = LoginForm(request.form)
    if session.get('user'):
        try:
            dynamodb.get_user(Id=session['user']['oid'])
        except ValueError:
            dynamodb.new_user(Id=session['user']['oid'])
    if form.validate_on_submit():
        flash('Login requested for user {}, password={}'.format(
            form.email.data, form.password.data))
    
    return render_template('login.html',title="VPN Registration",form=form,auth_url=session["flow"]["auth_uri"])

@app.route('/compare_faces', methods = ['POST'])
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
                    'Name': f'models/{session["user"]["name"]}.jpg',
                }
            },
            QualityFilter='NONE'
        )   
        print(response)
        if response['FaceMatches'][0]['Similarity'] >= 94:
            return "Match"
        else:
            return "NoMatch"
    except (ClientError,IndexError): # These errors are typically raised when a face isn't detected, isn't able to be processed etc
        return "NoMatch"
        

@app.route("/dashboard")
def dashboard():
    if not session.get("user"):
        return redirect(url_for('login'))
    with open("token.txt","w") as f:  # Debug
        f.write(str(session["user"]))
    return render_template('landing.html', user=session["user"], version=msal.__version__)


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
    return redirect(url_for('dashboard'))

@app.route("/ms-logout")
def ms_logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        config['AUTHORITY'] + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("landing", _external=True))



app.jinja_env.globals.update(ms_build_auth_code_flow=oauth2.ms_build_auth_code_flow)  # Used in template
