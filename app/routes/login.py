from base.main import *

@app.route('/login', methods =['GET', 'POST'])
def login():
    # check if user is in session
    if (session.get('loggedin') == True):
        flash('You are already login as user: ' + session.get('username'))
        return redirect('/')

    # check user is exist or not
    if request.method == 'POST' and 'username' in request.form and 'userPassword' in request.form:

        username = request.form['username']
        userPassword = request.form['userPassword']
        remember = request.form.getlist('remember')
        capcha = request.form['g-recaptcha-response']
        userPassword = encrypt(userPassword)
        
        # validate username
        if username is not None:
            if not validateInput(username) or not validateInput(userPassword):
                return('Bad input')

        # if user is in database, make a new session
        if capchaVerify(capcha, config('SECRET_CAPCHA_KEY')):
            conn = getDatabaseConnect(PATH)
            account = conn.execute('SELECT * FROM account WHERE username = ? AND userPassword = ?', (username, userPassword,)).fetchone()
            conn.close()
            if account:
                if remember:
                    # session last 1 week
                    makeSessionPermanent(43200)
                else:
                    # session last 5 minutes
                    makeSessionPermanent(5)

                session['loggedin'] = True
                session['id'] = account['userID']
                session['username'] = account['username']
                flash('Login successfully')
                return redirect(url_for('index'))
            else:
                flash('Incorrect username or password !')
                return redirect('/login')

        else:
            flash('Capcha error')
            return redirect('/login')
        
    return render_template('login.html', key = config('PUBLIC_CAPCHA_KEY'))

def capchaVerify(response, secret_key):
    user_ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    capcha = requests.get('https://www.google.com/recaptcha/api/siteverify?secret=' + secret_key + '&response=' + response + '&remoteip=' + user_ip_address)
    data = capcha.json()
    if data['success']:
        return True
    return False

# making session expired 
def makeSessionPermanent(expireTime):
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=expireTime)