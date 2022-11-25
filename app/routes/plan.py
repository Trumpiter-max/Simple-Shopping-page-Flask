from base.main import *

@app.route('/plan', methods=['GET', 'POST'])
def plan():
    if (session.get('loggedin') != True):
        flash('You need to login first')
        return redirect('/login')
    
    conn = getDatabaseConnect(PATH)

    # get current balance of user
    balance = conn.execute('SELECT balance FROM account WHERE userID = ?', (str(session.get('id')), )).fetchall()
    currentBalance = balance[0][0]

    check = conn.execute('SELECT tier FROM account WHERE userID = ?', (session.get('id'), )).fetchall()
    tier = check[0][0]
    if tier == 1:
        tier = 'Silver'
    elif tier == 2:
        tier = 'Gold'
    elif tier == 3:
        tier = 'Plantium'
    else:
        tier = 'Free'
        
    if request.method == 'POST':
        vip = request.args.get('becomevip')
        cancel = str(request.args.get('cancelvip'))

        # cancel plan
        if cancel == 'true':
            if tier != 'Free':
                resetMember(session.get('id'))
                # remove auto reset account
                sched.remove_job(str(session.get('id')))
                return redirect(url_for('user'))
            else:
                flash('Cancel failed')
                return redirect('/plan')

        # become member
        if tier != 'Free':
            return('You are already VIP member')
        elif type(vip) != 'NoneType':
            # tier 1: vip in 1 day
            if int(vip) == 1:
                if (float(currentBalance) < 50.0):
                    flash("Not enough money")
                becomeMember(1, currentBalance, 50.0, 1)
                return(redirect(url_for('plan')))
            # tier 2: vip in 30 day
            elif int(vip) == 2:
                if (float(currentBalance) < 100.0):
                    flash("Not enough money")
                becomeMember(2, currentBalance, 100.0, 30)
                return(redirect(url_for('plan')))
            # tier 3: vip in 365 day
            elif int(vip) == 3:
                if (float(currentBalance) < 500.0):
                    flash("Not enough money")
                becomeMember(3, currentBalance, 500.0, 365)
                return(redirect(url_for('plan')))
            else:
                flash('Bad request')
                return redirect('/plan')

    conn.close()        
    return render_template(('plan.html'), currentBalance=currentBalance, tier=tier)

def becomeMember(tier, currentBalance, money, day):
    if float(currentBalance) >= money:
        conn = getDatabaseConnect(PATH)
        # update database
        conn.execute('UPDATE account SET tier = ? WHERE userID = ?', (tier, session.get('id'), ))
        conn.execute('UPDATE account SET balance = ? WHERE userID = ?', (float(currentBalance) - money,session.get('id'),))
        conn.commit()
        conn.close()
        makeSchedule(day)

def makeSchedule(expireDay):
    # get date and time after excute
    today = datetime.today()
    date = today + expireDay*timedelta(1)
    date = str(date.strftime("%Y-%m-%d %H:%M:%S"))
    # execute the cron which reset user to free member
    sched.add_job(resetMember, 'date', run_date=date, args=[session.get('id')], id=str(session.get('id')))
    sched.start()

# after schedule, reset member to free member
def resetMember(id):
    conn = getDatabaseConnect(PATH)
    conn.execute('UPDATE account SET tier = 0 WHERE userID = ?', (id, ))
    conn.commit()
    conn.close()
