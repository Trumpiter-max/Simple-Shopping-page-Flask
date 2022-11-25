from base.main import *

@app.route('/balance', methods=['GET', 'POST'])
def balance():
    if (session.get('loggedin') != True):
        flash('You need to login first')
        return redirect('/balance')

    conn = getDatabaseConnect(PATH)

    # get current balance of user
    balance = conn.execute('SELECT balance FROM account WHERE userID = ?', (str(session.get('id')), )).fetchall()
    currentBalance = balance[0][0] 

    if request.method == 'POST' and 'credit' in request.form and 'userPassword' in request.form:

        credit = float(request.form['credit'])
        userPassword = request.form['userPassword']
        userPassword = encrypt(userPassword)

        check = conn.execute('SELECT * FROM account WHERE userID = ? AND userPassword = ?', (str(session.get('id')), userPassword, )).fetchone()
        if check and float(credit) > 0:
            conn.execute('UPDATE account SET balance = ? WHERE userID = ? AND userPassword = ? ',(float(currentBalance) + float(credit), session.get('id') ,userPassword,))
            conn.commit()
            flash('Added credit to your balance')
            return redirect(url_for('balance'))
        else:
            flash('Password or credit is invalid')
            return redirect('/balance')

    if request.method == 'POST' and 'destination' in request.form and 'userPassword' in request.form and 'money' in request.form:

        destination = int(request.form['destination'])
        money = float(request.form['money'])
        userPassword = request.form['userPassword']
        userPassword = encrypt(userPassword)

        if money > float(currentBalance) and money < 0.0:
            flash('Invalid amount')
            return redirect('/balance')

        # check if user is exist in database
        user = conn.execute('SELECT * FROM account WHERE userID = ?', (destination, )).fetchone()
        if user and destination != str(session.get('id')):
            # check password match with passwaord in database
            check = conn.execute('SELECT balance FROM account WHERE userID = ? AND userPassword = ?', (str(session.get('id')), userPassword, )).fetchone()
            if check:
                destination =  conn.execute('SELECT balance FROM account WHERE userID = ?', (destination, )).fetchall()
                destinationBalance = float(destination[0][0])
                # update current account
                conn.execute('UPDATE account SET balance = ? WHERE userID = ? AND userPassword = ? ',(currentBalance - money, session.get('id') ,userPassword,))
                # update destination's account
                conn.execute('UPDATE account SET balance = ? WHERE userID = ? ',(destinationBalance + money, destination,))
                conn.commit()
                flash('Transfer successfully')
                return redirect(url_for('index'))
        else:
            return('Invalid request')
    
    conn.close()        
    return render_template(('balance.html'), currentBalance=currentBalance)
