from functools import wraps
import re
from typing import Text
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request

from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, EmailField,  validators
from passlib.hash import sha256_crypt

app = Flask(__name__)


#MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'user'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#Init MySQL

mysql = MySQL(app)



@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def list_articles():

    #Cursor
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM articles")
    
    articles = cur.fetchall()

    if result:
        return render_template('articles.html', articles=articles)
    else:
        return render_template('articles.html')

    #Close connection    
    cur.close()


@app.route('/articles/<string:id>/')
def single_articles(id):

    #Cursor
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM articles where id=%s", (id))
    
    article = cur.fetchone()

    if result:
        return render_template('single-article.html', article=article)
    else:
        return render_template('single-article.html')

    #Close connection    
    cur.close()

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username  = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message="Password do not match")
        ])
    confirm = PasswordField('Confirm Password')
       


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if  request.method == "POST" and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = form.password.data
        enc_password = sha256_crypt.encrypt(str(password))

        #Cursor
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, username, password) values(%s, %s, %s, %s)", (name, email, username, enc_password))

        #Commit to db
        mysql.connection.commit()

        #Close db connection
        cur.close()

        flash("You are registered and can log in.", 'success')

        return redirect(url_for('login'))


    return render_template('register.html', form=form)


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == "POST":
        #Getting form data
        username = request.form.get('username')
        password = request.form.get('password')

        #Cursor
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username=%s", [username])

        if result > 0:
            #Get Hash
            data = cur.fetchone()
            real_password = data.get('password')

            #verify password
            if sha256_crypt.verify(password, real_password):
                session['logged_in']=True
                session['username']=username
                app.logger.info("Password matched")
                flash("You are logged in.", 'success')
                return redirect(url_for('dashboard'))
            else:
                app.logger.info("Password not matched")
                flash("Invalid credentials!", 'danger')

            #Close db connection
            cur.close()

        else:
            app.logger.info("User not found")  
            flash("User not found.", 'warning')  

    return render_template('login.html')    



#Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorised, Please login!", 'danger')
            return redirect(url_for('login'))    

    return wrap 


@app.route('/logout')
def logout():
    session.clear()
    flash("You are logged out.", 'success')
    return redirect(url_for('login'))



@app.route('/dashboard')
@is_logged_in
def dashboard():

    #Cursor
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM articles")

    articles = cur.fetchall()

    if result:
        return render_template('dashboard.html', articles=articles)
    else:
        return render_template('dashboard.html')

    #Close connection    
    cur.close()



class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    content  = TextAreaField('Content') 

@app.route('/add-article',methods=["GET","POST"])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if  request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data

        #Cursor
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO articles(title, content, author) values(%s, %s, %s)", (title, content, session['username']))

        #Commit to db
        mysql.connection.commit()

        #Close db connection
        cur.close()

        flash("New article added.", 'success')

        return redirect(url_for('dashboard'))


    return render_template('add-article.html',form=form)


@app.route('/edit-article/<string:id>',methods=["GET", "POST"])
@is_logged_in
def edit_article(id):

    #Cursor
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM articles where id=%s", (id))

    article = cur.fetchone() 
    cur.close()

    form = ArticleForm(request.form)
   
    #Populating data in form to edit
    form.title.data = article['title']
    form.content.data = article['content']

    if request.method == 'POST' and form.validate():
        title = request.form.get("title")
        content = request.form.get("content")

        #Cursor
        cur = mysql.connection.cursor()
        cur.execute("UPDATE articles SET title=%s, content=%s where id=%s", (title, content, id))

        #Commit to db
        mysql.connection.commit()
 
        #Close db connection
        cur.close()

        flash("Article updated.", 'success')

        return redirect(url_for('dashboard'))


    return render_template('edit-article.html',form=form)



@app.route('/delete-article/<string:id>')
@is_logged_in
def delete_article(id):

    #Cursor
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM articles WHERE id = %s", (id))
    
    #Commit to DB & Close
    mysql.connection.commit()
    cur.close()

    flash("Article deleted.", 'success')
    
    return redirect(url_for('dashboard'))







if __name__ == "__main__":
    app.secret_key = "my secret key"
    app.run(debug=True)