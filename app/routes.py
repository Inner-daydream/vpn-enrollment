import flask
import flask_login
from app import app
import app.oauth2 as oauth2
import boto3
import botocore.exceptions
import app.dynamodb as dynamodb
import app.forms as forms
import base64
import app.wireguard_management as wireguard
import io

with app.app_context():
    config = flask.current_app.config
    login_manager = flask.current_app.login_manager

@login_manager.user_loader
def load_user(user_id):
    try:
        user = dynamodb.User(user_id)
    except ValueError:
        user = None
    return user
    
@login_manager.unauthorized_handler
def unauthorized():
    return flask.redirect(flask.url_for('login'))

@app.route('/',methods=['GET','POST'])
def login():
    flask.session['facial_recognition'] = False
    flask.session["flow"] = oauth2.ms_build_auth_code_flow(
        scopes=config['SCOPE'],
        client_id=config['CLIENT_ID'],
        client_secret=config['CLIENT_SECRET'],
        authority=config['AUTHORITY']
    ) 
    form = forms.LoginForm(flask.request.form)
    if form.validate_on_submit():
        if dynamodb.validate_login(Id=form.email.data,password=form.password.data):
            user = dynamodb.User(id=form.email.data)
            flask_login.login_user(user)
            return flask.redirect(flask.url_for('dashboard'))
    return flask.render_template('login.html',title="VPN Registration",form=form,auth_url=flask.session["flow"]["auth_uri"])

@app.route('/compare_faces', methods = ['POST'])
@flask_login.login_required
def compare_faces():
    client = boto3.client('rekognition')
    jsdata = flask.request.form['javascript_data'][23:]
    try:
        response = client.compare_faces(
            SourceImage={
                'Bytes': base64.b64decode(jsdata)
            },
            TargetImage={
                'S3Object': {
                    'Bucket': 'vpnenrollment',
                    'Name': f'models/{flask_login.current_user.username}.jpg',
                }
            },
            QualityFilter='NONE'
        )   
        if response['FaceMatches'][0]['Similarity'] >= 98:
            flask.session['facial_recognition'] = True
            return "Match"
        else:
            return "NoMatch"
    except (botocore.exceptions.ClientError,IndexError,KeyError): # These errors are typically raised when a face isn't detected, isn't able to be processed etc
        return "NoMatch"
        
@app.route("/generate")
@flask_login.login_required
def generate():
    if not flask_login.current_user.facial_recognition:
        flask.redirect(flask.url_for(dashboard))
    peers = dynamodb.get_peers(Id=flask_login.current_user.id)
    return flask.render_template("generate.html",peers=peers)
@app.route("/dashboard")
@flask_login.login_required
def dashboard():
    return flask.render_template('landing.html', user=flask_login.current_user.username)
@app.route("/generate_configuration", methods=['POST'])
@flask_login.login_required
def generate_configuration():
    peer_name = flask.request.form['configuration_name']
    filename,client_configuration_string = wireguard.add_peer(Id=flask_login.current_user.id,peer_name=peer_name)
    return flask.send_file(path_or_file=io.BytesIO(bytes(client_configuration_string,'UTF-8')),download_name=filename,as_attachment=True)

@app.route("/revoke", methods=["POST"])
@flask_login.login_required
def revoke():
    peer_name = flask.request.form['peer_name']
    wireguard.remove_peer(Id=flask_login.current_user.id,peer_name=peer_name)
    return flask.redirect(flask.url_for("generate"))

@app.route(config['REDIRECT_PATH'])  # Its absolute URL must match your app's redirect_uri set in AAD
def ms_authorized():
    try:
        cache = oauth2.ms_load_cache(flask.session)
        result = oauth2.ms_build_msal_app(
            cache=cache,
            authority=config['AUTHORITY'],
            client_id=config['CLIENT_ID'],
            client_secret=config['CLIENT_SECRET']
            ).acquire_token_by_auth_code_flow(
            flask.session.get("flow", {}), flask.request.args)
        if "error" in result:
            return flask.render_template("auth_error.html", result=result)
        flask.session["user"] = result.get("id_token_claims")
        oauth2.ms_save_cache(cache=cache,session=flask.session)
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
    try:
        dynamodb.get_user(Id=flask.session['user']['oid'])
    except ValueError:
        dynamodb.new_user(Id=flask.session['user']['oid'])
    user = dynamodb.User(id=flask.session['user']['oid'])
    flask_login.login_user(user)
    return flask.redirect(flask.url_for('dashboard'))

@app.route("/ms-logout")
def ms_logout():
    flask.session.clear()  # Wipe out user and its token cache from session
    return flask.redirect(  # Also logout from your tenant's web session
        config['AUTHORITY'] + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + flask.url_for("login", _external=True))



app.jinja_env.globals.update(ms_build_auth_code_flow=oauth2.ms_build_auth_code_flow)  # Used in template
