from base.main import *

@app.route('/register', methods =['GET', 'POST'])
def register():
    # check if user is in database. If not, create new one
    if request.method == 'POST' and 'username' in request.form and 'userPassword' in request.form and 'email' in request.form :
        username = request.form['username']
        userPassword = request.form['userPassword']
        email = request.form['email']
        
        # check if account exist
        conn = getDatabaseConnect(PATH)
        check = conn.execute('SELECT * FROM account WHERE username = ? AND userPassword = ?',(username, userPassword, )).fetchone()
        
        if check:
            flash('Account already exists !')
            return redirect('/register')

        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address !')
            return redirect('/register')

        elif not re.match(r'[A-Za-z0-9]{4,}', username):
            flash('Username at least 4 characters must contain only characters and numbers !')
            return redirect('/register')

        elif not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', userPassword):
            flash('Password must contain at least 8 characters, at least one letter and one number')
            return redirect('/register')

        elif not username or not userPassword or not email:
            flash('Please fill out the form !')
            return redirect('/register')

        else:
            userPassword = encrypt(userPassword)
            conn.execute('INSERT INTO account (username, userPassword, email, balance, tier, avatarname) VALUES ( ?, ?, ?, 0.0, 0, "default.jpg")', (username, userPassword, email, ))
            conn.commit()
            conn.close()
            flash('You have successfully registered !')
            return redirect(url_for('login'))
        
    elif request.method == 'POST':
        flash('Please fill out the form !')
        return redirect('/register')

    return render_template('register.html')