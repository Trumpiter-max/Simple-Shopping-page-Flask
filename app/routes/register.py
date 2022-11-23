from base.main import *

@app.route('/register', methods =['GET', 'POST'])
def register():
    # check if user is in database. If not, create new one
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'pw' in request.form and 'email' in request.form :
        username = request.form['username']
        pw = request.form['pw']
        email = request.form['email']
        pw = encrypt(pw)

        # check if account exist
        conn = get_db_connection(PATH)
        check = conn.execute('SELECT * FROM account WHERE username = ? AND pw = ?',(username, pw, )).fetchone()
        if check:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not pw or not email:
            msg = 'Please fill out the form !'
        else:
            
            conn = get_db_connection(PATH)
            conn.execute('INSERT INTO account (username, pw, email, balance, tier, avatarname) VALUES ( ?, ?, ?, 0, 0, "default.jpg")', (username, pw, email, ))
            conn.commit()
            msg = 'You have successfully registered !'
            return redirect('/')

        conn.close()

    elif request.method == 'POST':
        msg = 'Please fill out the form !'

    return render_template('register.html', msg = msg)