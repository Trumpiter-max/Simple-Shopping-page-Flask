from base.main import *

@app.route('/user', methods=['GET', 'POST'])
def user():
    if (session.get('loggedin') != True):
        flash('You need to login first')
        return redirect('/login')

    conn = getDatabaseConnect(PATH)
    userData = conn.execute('SELECT email, firstname, lastname, useraddress, avatarname, tier, phone FROM account WHERE userID = ?', (session.get('id'), )).fetchall()

    # get data from user data
    mail = userData[0][0]
    firstname = userData[0][1]
    lastname = userData[0][2]
    useraddress = userData[0][3]
    avatarname = userData[0][4]
    tier = int(userData[0][5])
    phone = userData[0][6]

    if tier == 1:
        tier = 'Silver'
    elif tier == 2:
        tier = 'Gold'
    elif tier == 3:
        tier = 'Plantium'
    else:
        tier = 'Free'

    if request.method == "GET":
        firstname = request.args.get('firstname')
        lastname = request.args.get('lastname')
        useraddress = request.args.get('address')
        email = request.args.get('email')
        phone = request.args.get('phone')

        # update detail of user
        if firstname is not None and firstname != '':
            if not re.match(r'[A-Za-z]+', firstname):
                flash('first name is invalid')
                return redirect('/user')
            else:
                updatedata('firstname', firstname)

        if lastname is not None and lastname != '':
            if not re.match(r'[A-Za-z]+', lastname):
                flash('last name is invalid')
                return redirect('/user')
            else:
                updatedata('lastname', lastname)

        if useraddress is not None and useraddress != '':
            if not re.match(r'[A-Za-z0-9]+',useraddress):
                flash('address is invalid')
                return redirect('/user')
            else:
                updatedata('useraddress', useraddress)
        
        if email is not None and email != '':
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                flash('email is invalid')
                return redirect('/user')
            else:
                updatedata('email', email)

        if phone is not None and phone != '':
            if not re.match(r"^[0-9\-\+]{10,11}$", phone):
                flash('phone number is invalid')
                return redirect('/user')
            else:
                updatedata('phone', phone)

        if firstname or lastname or useraddress or email or phone:
            flash('Update successfuly')
            return(redirect(url_for('user')))

    # change password
    if request.method == "POST" and 'olduserPassword' in request.form and 'newuserPassword' in request.form:
        oldUserPassword = request.form['olduserPassword']
        oldUserPassword = encrypt(oldUserPassword)
        newUserPassword = request.form['newuserPassword']

        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', newUserPassword):
            flash('Password must contain at least eight characters, at least one letter and one number')
            return(redirect(url_for('user')))

        newUserPassword = encrypt(newUserPassword)
        conn = getDatabaseConnect(PATH)
        check = conn.execute('SELECT * FROM account WHERE userID = ? AND userPassword = ?',(session.get('id'), oldUserPassword, )).fetchone()

        if check:
            conn.execute('UPDATE account SET userPassword = ? WHERE userID = ?', (newUserPassword, session.get('id'), ))
            conn.commit()
        conn.close()
        
    # process upload avatar
    if request.method == 'POST':
        uploadFile()
        return(redirect(url_for('user')))

    
    return render_template(('user.html'), firstname=firstname, lastname=lastname, useraddress=useraddress, avatarname=avatarname, tier=tier, mail=mail, phone=phone)

def updatedata(name, data):
    conn = getDatabaseConnect(PATH)
    conn.execute('UPDATE account SET ' + str(name) + ' = ? WHERE userID = ?', (str(data), session.get('id'), ))
    conn.commit()
    conn.close()

def uploadFile():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        return redirect(request.url)
    if file and allowedFile(file.filename):

        # check if user has avatar already
        conn = getDatabaseConnect(PATH)

        # delete old photo
        oldfile = conn.execute('SELECT avatarname FROM account WHERE userID = ?', (session.get('id'), )).fetchall()
        if oldfile and oldfile[0][0] != 'default.jpg':
            os.remove(IMG_PATH+'/avatar/'+oldfile[0][0])

        filename = secure_filename(file.filename)
        file.save(os.path.join(IMG_PATH + '/avatar', filename))
        
        conn.execute('UPDATE account SET avatarname = ? WHERE userID = ?', (filename, session.get('id'), ))
        conn.commit()
        conn.close()
    else:
        flash('file is not allowed') 
        return redirect(request.url)


        
