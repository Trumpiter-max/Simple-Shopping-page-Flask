from base.main import *

@app.route('/cart')
def cart():
    # this feature is not already
    if (session.get('loggedin') != True):
        flash('You need to login first')
        return redirect('/login')

    status = ''

    # show current user's balance
    conn = getDatabaseConnect(PATH)
    balance = conn.execute('SELECT balance FROM account WHERE userID = ?', (session.get('id'), )).fetchall()
    currentBalance = balance[0][0] 

    cart = conn.execute('SELECT * FROM cart JOIN product USING (productID) WHERE userID = ?',(session.get('id'), )).fetchall()
    
    # find total price of all product in cart
    temp = conn.execute('SELECT SUM(total) FROM cart WHERE userID = ?',(session.get('id'), )).fetchall()
    totalPrice = temp[0][0] if temp[0][0] is not None else 0

    # check if user is vip member
    isVIP = conn.execute('SELECT tier FROM account WHERE userID = ?', (str(session.get('id')), )).fetchall()
    conn.close()
    vip = int(isVIP[0][0])

    if vip > 0:
        status = "VIP exclusive right: 30 percent discount"
        totalPrice = str(float(totalPrice)*70/100)

    if request.method == 'GET' :
        action = request.args.get('action')

        if action == 'CheckOut':
            if totalPrice is None:
                flash('There is no item in cart')
            if currentBalance < totalPrice:
                flash('Not enough money')
            checkOut(float(currentBalance), float(totalPrice))
            # clear cart after checkout
            clearCart()
            return redirect('/cart')

        elif action == 'ClearCart':
            if totalPrice is None:
                flash('There is no item in cart')
            clearCart()
            return redirect('/cart')

    return render_template('cart.html', cart=cart, totalPrice=totalPrice, currentBalance=currentBalance, status=status)

def checkOut(currentBalance, totalPrice):
    conn = getData(PATH)
    con = getDatabaseConnect(PATH)
    listProduct = conn.execute('SELECT productID, productQuantity FROM cart WHERE userID = ?', (session.get('id'), )).fetchall()
    for value in listProduct:
        temp = conn.execute('SELECT quantity FROM product WHERE productID = ?', (value[0], )).fetchone()
        quantity = temp[0]
        con.execute('UPDATE product SET quantity = ? WHERE productID = ?',(int(quantity) - int(value[1]), value[0] ))

    # update balance after cheking out    
    con.execute('UPDATE account SET balance = ? WHERE userID = ?',(currentBalance - totalPrice, session.get('id'), ))
    con.commit()

    conn.close()
    con.close()

def clearCart():
    conn = getDatabaseConnect(PATH)
    conn.execute('DELETE FROM cart WHERE userID = ?', (session.get('id'), ))
    conn.commit()
    conn.close()