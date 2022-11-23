from base.main import *

@app.route('/user', methods=['GET', 'POST'])
def user():
    if (session.get('loggedin') != True):
        return('You need to login first')

    conn = get_db_connection(PATH)
    user_data = conn.execute('SELECT * FROM account WHERE userID = ?', (session.get('id'), )).fetchall()
    
    # get data from user data
    mail = user_data[0][3]
    firstname = user_data[0][4]
    lastname = user_data[0][5]
    useraddress = user_data[0][6]
    avatarname = user_data[0][7]
    tier = int(user_data[0][9])
    phone = user_data[0][10]
    
    if tier == 1:
        tier = 'Silver'
    elif tier == 2:
        tier = 'Gold'
    elif tier == 3:
        tier = 'Plantium'
    else:
        tier = 'Free'

    if request.method == "GET":
        fname = request.args.get('firstname')
        lname = request.args.get('lastname')
        uaddress = request.args.get('address')
        email = request.args.get('email')
        phone = request.args.get('phone')

        # update detail of user
        if fname != None and fname != '':
            if not re.match(r'[A-Za-z]+', fname):
                return('first name is invalid')
            updatedata('firstname', fname)

        if lname != None and lname != '':
            if not re.match(r'[A-Za-z]+', lname):
                return('last name is invalid')
            updatedata('lastname', lname)

        if uaddress != None and uaddress != '':
            if not re.match(r'[A-Za-z0-9]+',uaddress):
                return('address is invalid')
            updatedata('useraddress', uaddress)
        
        if email != None and email != '':
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                return('email is invalid')
            updatedata('useraddress', uaddress)

        if phone != None and phone != '':
            if not re.match(r"^[0-9\-\+]{10,11}$", phone):
                return('phone number is invalid')
            updatedata('useraddress', uaddress)

        if fname or lname or uaddress or email or phone:
            return redirect('/user')

    # change password
    if request.method == "POST" and 'oldpw' in request.form and 'newpw' in request.form:
        oldpw = request.form['oldpw']
        oldpw = encrypt(oldpw)
        newpw = request.form['newpw']
        newpw = encrypt(newpw)
        
        conn = get_db_connection(PATH)
        check = conn.execute('SELECT * FROM account WHERE userID = ? AND pw = ?',(session.get('id'), oldpw, )).fetchone()

        if check:
            conn.execute('UPDATE account SET pw = ? WHERE userID = ?', (newpw, session.get('id'), ))
            conn.commit()

        conn.close()
    # process upload avatar
    if request.method == 'POST':
        upload_file()
        return redirect('/user')
     
    conn.close()
    return render_template(('user.html'), firstname=firstname, lastname=lastname, useraddress=useraddress, avatarname=avatarname, tier=tier, mail=mail, phone=phone)

def updatedata(name, data):
    conn = get_db_connection(PATH)
    conn.execute('UPDATE account SET ' + str(name) + ' = ? WHERE userID = ?', (str(data), session.get('id'), ))
    conn.commit()
    conn.close()

def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):

        # check if user has avatar already
        conn = get_db_connection(PATH)

        # delete old photo
        oldfile = conn.execute('SELECT avatarname FROM account WHERE userID = ?', (session.get('id'), )).fetchall()
        if oldfile and oldfile[0][0] != 'default.jpg':
            os.remove(IMG_PATH+'/avatar/'+oldfile[0][0])

        filename = secure_filename(file.filename)
        file.save(os.path.join(IMG_PATH + '/avatar', filename))
        
        conn.execute('UPDATE account SET avatarname = ? WHERE userID = ?', (filename, session.get('id'), ))
        conn.commit()
        conn.close()


        
