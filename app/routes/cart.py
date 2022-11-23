from base.main import *

@app.route('/cart')
def cart():
    # this feature is not already
    if (session.get('loggedin') != True):
        return('You need to login first')

    msg = ''

    # show current user's balance
    conn = get_db_connection(PATH)
    balance = conn.execute('SELECT balance FROM account WHERE userID = ?', (session.get('id'), )).fetchall()
    current_balance = balance[0][0]

    cart = conn.execute('SELECT * FROM cart JOIN product USING (productID) WHERE userID = ?',(session.get('id'), )).fetchall()
    
    # find total price of all product in cart
    tmp = conn.execute('SELECT SUM(total) FROM cart WHERE userID = ?',(session.get('id'), )).fetchall()
    total_price = tmp[0][0]

    # check if user is vip member
    isVIP = conn.execute('SELECT tier FROM account WHERE userID = ?', (str(session.get('id')), )).fetchall()
    vip = int(isVIP[0][0])

    if vip > 0:
        msg = "VIP exclusive right: 30 percent discount"
        total_price = str(float(total_price)*70/100)

    if request.method == 'GET' :
        action = request.args.get('action')

        if action == 'CheckOut':
            if total_price == None:
                return('There is no item in cart')
            if current_balance < total_price:
                return('Not enough money')
            checkOut(float(current_balance), float(total_price))
            # clear cart after checkout
            clearCart()
            return redirect('/cart')

        elif action == 'ClearCart':
            if total_price == None:
                return('There is no item in cart')
            clearCart()
            return redirect('/cart')
   
    conn.close()
    return render_template('cart.html', cart=cart, total_price=total_price, current_balance=current_balance, msg=msg)

def checkOut(current_balance, total_price):
    conn = get_data(PATH)
    con = get_db_connection(PATH)
    list_product = conn.execute('SELECT productID, productQuantity FROM cart WHERE userID = ?', (session.get('id'), )).fetchall()
    for value in list_product:
        tmp = conn.execute('SELECT quantity FROM product WHERE productID = ?', (value[0], )).fetchone()
        quantity = tmp[0]

        con.execute('UPDATE product SET quantity = ? WHERE productID = ?',(int(quantity) - int(value[1]), value[0] ))
       
    # update balance after cheking out    
    con.execute('UPDATE account SET balance = ? WHERE userID = ?',(current_balance - total_price, session.get('id'), ))
    con.commit()

    conn.close()
    con.close()

def clearCart():
    conn = get_db_connection(PATH)
    conn.execute('DELETE FROM cart WHERE userID = ?', (session.get('id'), ))
    conn.commit()
    conn.close()