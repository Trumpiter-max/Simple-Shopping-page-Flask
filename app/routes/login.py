from base.main import *

@app.route('/login', methods =['GET', 'POST'])
def login():
    # check if user is in session
    if (session.get('loggedin') == True):
        return('You are already login as user: ' + session.get('username'))

    # check user is exist or not
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'pw' in request.form:

        username = request.form['username']
        pw = request.form['pw']

        remember = request.form.getlist('remember')

        capcha = request.form['g-recaptcha-response']
        pw = encrypt(pw)
        
        # validate username
        if username != None:
            if not validate_input(username) or not validate_input(pw):
                return('Bad input')

        # if user is in database, make a new session
        if capchaVerify(capcha, config('SECRET_CAPCHA_KEY')):
            conn = get_db_connection(PATH)
            account = conn.execute('SELECT * FROM account WHERE username = ? AND pw = ?', (username, pw,)).fetchone()
            if account:
                
                if remember:
                    # session last 1 week
                    make_session_permanent(43200)
                else:
                    # session last 5 minutes
                    make_session_permanent(5)

                session['loggedin'] = True
                session['id'] = account['userID']
                session['username'] = account['username']
                msg = 'Login successfully'
                return redirect(url_for('index'))
            else:
                msg = 'Incorrect username or password !'
        else:
            return('Capcha error')
        conn.close()

    return render_template('login.html', msg = msg, key = config('PUBLIC_CAPCHA_KEY'))

def capchaVerify(response, secret_key):
    user_ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    capcha = requests.get('https://www.google.com/recaptcha/api/siteverify?secret=' + secret_key + '&response=' + response + '&remoteip=' + user_ip_address)
    data = capcha.json()
    if data['success']:
        return True
    return False

# making session expired 
def make_session_permanent(time):
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=time)