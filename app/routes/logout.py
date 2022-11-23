from base.main import *

@app.route('/logout')
def logout():
    if (session.get('loggedin') != True):
        return('You need to login first')

    # pop user data from session 
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.clear() # clear cookie
    return redirect('/')