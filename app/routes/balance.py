from base.main import *

@app.route('/balance', methods=['GET', 'POST'])
def balance():
    if (session.get('loggedin') != True):
        return('You need to login first')

    msg = ''
    conn = get_db_connection(PATH)

    # get current balance of user
    balance = conn.execute('SELECT balance FROM account WHERE userID = ?', (str(session.get('id')), )).fetchall()
    current_balance = balance[0][0]

    if request.method == 'POST' and 'credit' in request.form and 'pw' in request.form:

        credit = float(request.form['credit'])
        pw = request.form['pw']
        pw = encrypt(pw)

        check = conn.execute('SELECT * FROM account WHERE userID = ? AND pw = ?', (str(session.get('id')), pw, )).fetchone()
        if check and float(credit) > 0:
            conn.execute('UPDATE account SET balance = ? WHERE userID = ? AND pw = ? ',(float(current_balance) + float(credit), session.get('id') ,pw,))
            conn.commit()
            msg = 'Added credit to your balance'
            return redirect(url_for('balance'))
        else:
            return('Password or credit is invalid')

    if request.method == 'POST' and 'destination' in request.form and 'pw' in request.form and 'money' in request.form:

        destination = int(request.form['destination'])
        money = float(request.form['money'])
        pw = request.form['pw']
        pw = encrypt(pw)

        if money > float(current_balance) and money < 0.0:
            return('Invalid amount')

        # check if user is exist in database
        user = conn.execute('SELECT * FROM account WHERE userID = ?', (destination, )).fetchone()
        if user and destination != str(session.get('id')):
            # check password match with passwaord in database
            check = conn.execute('SELECT balance FROM account WHERE userID = ? AND pw = ?', (str(session.get('id')), pw, )).fetchone()
            if check:
                des =  conn.execute('SELECT balance FROM account WHERE userID = ?', (destination, )).fetchall()
                des_balance = float(des[0][0])
                # update current account
                conn.execute('UPDATE account SET balance = ? WHERE userID = ? AND pw = ? ',(current_balance - money, session.get('id') ,pw,))
                # update destination's account
                conn.execute('UPDATE account SET balance = ? WHERE userID = ? ',(des_balance + money, destination,))
                conn.commit()
                msg = 'Transfer successfully'
                return redirect(url_for('index'))
        else:
            return('Invalid request')
    
    conn.close()        
    return render_template(('balance.html'), current_balance=current_balance, msg = msg)
