from flask import Flask,render_template,flash,redirect,url_for,request,session
from content_management import content
import sqlite3 as sql
from passlib.hash import sha256_crypt
from functools import wraps
from dbconnect import connection
TOPIC_DICT=content()

app=Flask(__name__)
app.secret_key = 'my unobvious secret key'
@app.route('/')
def home():
    return render_template('main.html')

@app.route('/dashboard/')
def dashboard():
    flash("flashed")
    return render_template('dashboard.html',TOPIC_DICT=TOPIC_DICT)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.route('/login/', methods=["GET", "POST"])
def login():
    error = ''
    return render_template("login.html", error=error)


# this login_required function is a function that chks if the user is logged in or not
# and contains a function f and login_required function is used to make sure that user is logged in to perform certail activities
# like to logout user should be logged in,to change password/sensitive data user need to reenter password .

def login_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash("you need to login first")
            return redirect(url_for('login'))
    return wrap
@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("you have been logged out")
    return redirect(url_for('dashboard'))
@app.route('/verrec',methods=['GET','POST'])
def verrec():
    error = ''
    try:
        c, con = connection()
        if request.method == "POST":
            usr=request.form['username']
            data = c.execute("SELECT * FROM ur WHERE username = (?)",
                             (usr,))

            data = c.fetchone()[2]

            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in'] = True
                session['username'] = usr

                # flash("You are now logged in")
                return redirect(url_for('dashboard'))

            else:
                error = "Invalid credentials, try again."

        # gc.collect()

        return render_template("login.html", error=error)

    except Exception as e:
        flash(e)
        error = "Invalid credentials, try again."
        return render_template("login.html", error=error)


@app.route('/register/',methods=['GET','POST'])
def register():
     return render_template('register.html')



@app.route('/addrec',methods=['GET','POST'])
def addrec():
    if request.method == 'POST':
        try:
            username=request.form['Username']
            email=request.form['email']
            password=sha256_crypt.encrypt(str(request.form['password']))
            reppassword=sha256_crypt.encrypt(str(request.form['reppassword']))
            c,con=connection()
            c.execute("CREATE TABLE IF NOT EXISTS ur(username TEXT,email Text,password TEXT,reppassword TEXT)")
            c.execute("INSERT INTO ur (username,email,password,reppassword) VALUES(?,?,?,?)", (username, email, password, reppassword))
            con.commit()
            flash("Thanks for registering")
        except:
            con.rollback()
            msg = "error"

        finally:
            return redirect(url_for('dashboard'))
        con.close()



if __name__ == "__main__":
    app.run(debug=True,port='8000')



