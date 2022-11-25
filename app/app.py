# import essential library and basic module
from base.main import * 

# import routes
from routes.login import *
from routes.register import *
from routes.logout import *
from routes.cart import *
from routes.user import *
from routes.balance import *
from routes.plan import *

# use for keeping client-side secure - encrypt cookie and save them to browser
app.config["SECRET_KEY"] = config('SECRET_KEY')

@app.route('/', methods = ['POST', 'GET'])
def index():
    conn = getDatabaseConnect(PATH)
    if request.method == 'POST':
        # using for authenticate valid session
        if (session.get('loggedin') == True): 
            # getting value from client
            number = int(request.form.get('number'))
            name = request.form.get('name')

            # query from table to find suit product
            temp = conn.execute('SELECT * FROM product WHERE productID = ?',(name, )).fetchall()
            defaultNumber = temp[0][4]
            price = temp[0][3]

            # validate input
            if not validateInput(name):
                return('Invalid name')

            # check valid request
            if (number <= 0) or (number > defaultNumber):
                flash("Invalid number of product")
                return redirect('/')
            
            # add value to session for using in cart later
            # check if product is exist in database
            check = conn.execute('SELECT * FROM cart WHERE userID = ? AND productID = ?', (session.get('id'), name, )).fetchone()
            if check:
                # if exist
                conn.execute('UPDATE cart SET productQuantity = ?, total = ? WHERE productID = ? AND userID = ?',(number, float(number*price), name, session.get('id'), ))
                conn.commit()
                flash('Update cart successfully')
                return redirect('/')
            else:
                # not exist
                conn.execute('INSERT INTO cart (userID, productID, productQuantity, total) VALUES (?, ?, ?, ?)', (session.get('id'), name, number, number*price, ))
                conn.commit()
                flash('Added to cart')
                return redirect('/')

        else:
            return('You need to login first')

    # using for listing all available product
    product = conn.execute('SELECT * FROM product').fetchall()
    conn.close()
    return render_template(('index.html'), product=product)

if __name__ == '__main__':
    sched.start()
    app.run()