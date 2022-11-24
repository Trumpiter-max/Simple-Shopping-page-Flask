from base.main import *

@app.route('/plan', methods=['GET', 'POST'])
def plan():
    if (session.get('loggedin') != True):
        return('You need to login first')
    
    conn = get_db_connection(PATH)

    # get current balance of user
    balance = conn.execute('SELECT balance FROM account WHERE userID = ?', (str(session.get('id')), )).fetchall()
    current_balance = balance[0][0]

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
                return('Cancel failed')

        # become member
        if tier != 'Free':
            return('You are already VIP member')
        elif type(vip) != 'NoneType':
            # tier 1: vip in 1 day
            if int(vip) == 1:
                if (float(current_balance) < 50.0):
                    return("Not enough money")
                becomeMember(1, current_balance, 50.0, 1)
                return(redirect(url_for('plan')))
            # tier 2: vip in 30 day
            elif int(vip) == 2:
                if (float(current_balance) < 100.0):
                    return("Not enough money")
                becomeMember(2, current_balance, 100.0, 30)
                return(redirect(url_for('plan')))
            # tier 3: vip in 365 day
            elif int(vip) == 3:
                if (float(current_balance) < 500.0):
                    return("Not enough money")
                becomeMember(3, current_balance, 500.0, 365)
                return(redirect(url_for('plan')))
            else:
                return('Bad request')
              
    conn.close()        
    return render_template(('plan.html'), current_balance=current_balance, tier=tier)

def becomeMember(tier, current_balance, money, day):
    if float(current_balance) >= money:
        conn = get_db_connection(PATH)
        # update database
        conn.execute('UPDATE account SET tier = ? WHERE userID = ?', (tier, session.get('id'), ))
        conn.execute('UPDATE account SET balance = ? WHERE userID = ?', (float(current_balance) - money,session.get('id'),))
        conn.commit()
        conn.close()
        makeSchedule(day)
   
def makeSchedule(day):
    # get date and time after excute
    today = datetime.today()
    date = today + day*timedelta(1)
    date = str(date.strftime("%Y-%m-%d %H:%M:%S"))
    # execute the cron which reset user to free member
    sched.add_job(resetMember, 'date', run_date=date, args=[session.get('id')], id=str(session.get('id')))
    sched.start()

# after schedule, reset member to free member
def resetMember(id):
    conn = get_db_connection(PATH)
    conn.execute('UPDATE account SET tier = 0 WHERE userID = ?', (id, ))
    conn.commit()
    conn.close()
