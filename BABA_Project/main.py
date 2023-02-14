from ast import Sub
from crypt import methods
from pyexpat.errors import messages
from sqlite3 import Cursor
from types import NoneType
from unittest import result
from xml.dom.minidom import Document
from sqlalchemy import true
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_wtf.file import FileField
#from flask_api import Form     
from wtforms import SubmitField
#from flask_wtf import Form
from flask_wtf import FlaskForm as Form
from flask_mysqldb import MySQL
import MySQLdb.cursors
import config
from io import BytesIO
import chardet

selectedBook = 0

app = Flask(__name__)

app.config['MYSQL_HOST'] = config.host
app.config['MYSQL_USER'] = config.user
app.config['MYSQL_PASSWORD'] = config.password
app.config['MYSQL_DB'] = config.db
app.config['MYSQL_PORT'] = config.port

mysql = MySQL(app)

register_book = "INSERT INTO admin_loads(author, description, book_id, file_data) VALUES (%s,%s,%s,%s)"
upload_book = "INSERT INTO books(book_id, author, book_title, content) VALUES (%s,%s,%s,%s)"       #for blob data file.read()funct,on is used
check_book_duplicate = "SELECT book_title FROM books WHERE book_title =(%s) "
member_exist = "SELECT email FROM members WHERE email = %s"
member_login = "SELECT first_name, last_name, password, email FROM members WHERE first_name=%s AND last_name=%s AND password=%s AND email=%s"
admin_login = "SELECT first_name, last_name, password FROM admins WHERE first_name = %s AND last_name = %s AND password = %s"
register_member = "INSERT INTO members(first_name, last_name, password, email) VALUES (%s,%s,%s,%s)"


admin_name = ""

class UploadForm(Form):
    file = FileField()
    submit = SubmitField("submit")
    download = SubmitField("indir")


@app.route("/",methods=['GET','POST'])
def start_page():
    if(request.method == 'POST'):
        if(request.form.get("buttonAdmin")=="Clicked"):
            return redirect("/admin")
        if(request.form.get("buttonMember")=="Clicked"):
            return redirect("/member")
   
    return render_template('about_us.html')



@app.route('/member', methods=['GET', 'POST'])
def member():
    if request.method == 'POST':
        userDetails = request.form
        name = userDetails['name']
        surname = userDetails['surname']
        password = userDetails['password']
        email = userDetails['email']
        select_data = (name,surname,password,email)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if( cursor.execute(member_login,select_data) ==True):
            cursor.close()
            return redirect("/search")
        else:
            print("Login was not successful")
    return render_template('member_login.html')



@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        userDetails = request.form
        name = userDetails['name']
        surname = userDetails['surname']
        password = userDetails['password']
        cursor = mysql.connection.cursor()
        cursor.execute(admin_login, (name, surname, password))
        account = cursor.fetchone()
        
        if account:
            session['loggedin'] = True
            print("Logged in")
            admin_name = name + surname
            form = UploadForm()
            return redirect('/book_register')
        return render_template('admin_login.html')
    return render_template('admin_login.html')

'''@app.route("/users")
def users():
    cursor = mysql.connection.cursor()
    resultValue = cursor.execute("SELECT * FROM users")
    if resultValue > 0:
        userDetails = cursor.fetchall()
        cursor.close()
        return render_template('users.html', userDetails=userDetails)
    return render_template('admin_login.html')'''



@app.route("/books", methods=['GET','POST'])
def books():
    cursor = mysql.connection.cursor()
    count = cursor.execute("SELECT book_title,author,content,book_id FROM books")
    
    if count > 0:
        book_tuple = cursor.fetchall()
        file_data = book_tuple[0][2]
        """book_list = list(list(book_tuple[0]))
        book_list[1] = "author"
        new_tuple = tuple([book_list[0],book_list[1]])
        print(new_tuple[1]," *** ", new_tuple[0])"""
        cursor.close()
        if(request.method=="POST"):
            book_id = int(request.form.get('download_button')) - 1
            print(book_id)
            return send_file(BytesIO(book_tuple[book_id][2]), download_name=book_tuple[book_id][0], as_attachment=True)

        return render_template('books.html', book_list=book_tuple)
    return render_template('main.html')



@app.route("/book_register", methods=['GET','POST'])
def book_register():
    form = UploadForm()
    if(request.method=='POST'):
        if form.validate_on_submit():
            if 'form2' in request.form:
                print(" *** ")
            if 'form1' in request.form:
                print(" &&& ")
            print(request.form)
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            files = form.file.data   
            if(files!=None):   
                book_name = files.filename
                book_binary = files.read()
                book_id = cursor.execute("SELECT * FROM books") + 1
                book_author = request.form['author']
                book_data = (book_id,book_author,book_name,book_binary)
                
                cursor.execute(upload_book,book_data)

                mysql.connection.commit()
                cursor.close()
            return redirect(url_for('book_register'))
        print(form.errors)
    return render_template('insert.html',form=form)



'''@app.route("/load_book", methods=['GET', 'POST'])
def load_book():
    if(request.method=='POST'):
        new_file = request.files['loaded_book']
        new_book = request.form
        binaryData = new_file.read()
        insert_data = (new_book['Author'], new_book['Description'], new_book['Book ID'], binaryData)
        cursor = mysql.connection.cursor()
        result = cursor.execute(register_book,insert_data)
        mysql.connection.commit()
    return render_template('book_register.html')'''



@app.route("/member_register",methods=["GET","POST"])
def member_register():
    if(request.method == "POST"):
        name = request.form['firstname']
        surname = request.form['surname']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor()
        insert_data = (name,surname,password,email)
        if(cursor.execute(member_exist,[email]) == False):
            insert_data = (name,surname,password,email)
            cursor.execute(register_member,insert_data)
            mysql.connection.commit()
            return redirect("/member")
        else:
            print("Member exists")
            flash("Member exists")
    return render_template("member_register.html")



'''@app.route("/download_book",methods=['GET','POST'])
def download_book():
    form = UploadForm()
    if(request.method=='POST'):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        count = cursor.execute("SELECT * FROM books")
        if count > 0:
            files = cursor.fetchall()
            file_name = files[0]['book_title']
            file_content = files[0]['content']

            mysql.connection.commit()
            cursor.close()

            return send_file(BytesIO(file_content), download_name=file_name, as_attachment=True)
        else:
            return render_template('book_register2.html',form=form)
    return render_template('book_register2.html',form=form)'''



@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        if 'book' in request.form:
            print("First Form is Clicked")
            form = UploadForm()
            book = request.form['book']
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT book_title, author, content, book_id from books WHERE book_title = %s OR author = %s", (book, book))
            result = mysql.connection.commit()
            data = cursor.fetchall()

            if len(data) == 0 and book == 'all': 
                cursor.execute("SELECT book_title, author, content, book_id from books")
                mysql.connection.commit()
                data = cursor.fetchall()

            elif len(data) > 0:
                if request.form.get('download_button') != None:
                    book_id = int(request.form.get('download_button')) - 1
                    return send_file(BytesIO(data[book_id][2]), download_name=data[book_id][0], as_attachment=True)
            return render_template('searchBar.html', data=data, form=form, book=book)

        elif 'downloadBook' in request.form:
            if request.form.get('downloadBook') != None:
                    selectedBook = int(request.form.get('downloadBook')) 
                    return redirect(url_for('book_detailed',bookIndex = selectedBook))

    return render_template('searchBar.html')



@app.route("/book_detailed/<bookIndex>",methods=['GET','POST'])
def book_detailed(bookIndex):
    form = UploadForm()
    if(bookIndex!=0):    
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        count = cursor.execute("SELECT book_title,author,content FROM books WHERE book_id = %s",str(bookIndex))
        if count > 0:
            files = cursor.fetchall()
            file_name = files[0]['book_title']
            file_author = files[0]['author']
            file_content = files[0]['content']
            i = 0
            while(file_name[-i]!='.'):
                i = i + 1
            book_name = file_name[0:-i]
            print(file_name)

            mysql.connection.commit()
            cursor.close()
            if(request.method=='POST'):
                return send_file(BytesIO(file_content), download_name=file_name, as_attachment=True)
            else:
                return render_template('selectedBook.html',data = [(book_name,files[0]['author'])])
        return render_template('selectedBook.html',data = (book_name,files[0]['author']))
    return render_template('selectedBook.html')



'''@app.route('/searched', methods=['GET', 'POST'])
def searched():
    if request.method == "POST":
        form = UploadForm()
        book = request.form['book']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT book_title, author, content, book_id from books WHERE book_title = %s OR author = %s", (book, book))
        result = mysql.connection.commit()
        data = cursor.fetchall()
        if len(data) == 0 and book == 'all': 
            cursor.execute("SELECT book_title, author from books")
            mysql.connection.commit()
            data = cursor.fetchall()
        elif len(data) > 0:
            if request.form.get('download_button') != None:
                book_id = int(request.form.get('download_button')) - 1
                print(book_id)
                return send_file(BytesIO(data[book_id][2]), download_name=data[book_id][0], as_attachment=True)
        return render_template('searchBar.html', data=data, form=form)
    return render_template('searchBar.html')'''

if __name__ == '__main__':
    app.secret_key = 'Beni Anla Bana Anlat'
    app.run(debug=true)
   