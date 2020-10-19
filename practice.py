from flask import *
import numpy as np
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL


app = Flask(__name__)

app.config['MYSQL_HOST']= 'localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='root'
app.config['MYSQL_DB']='books'
mysql = MySQL(app)

books = pd.read_csv('BX-Books.csv', sep=',', error_bad_lines=False, encoding="latin-1")
#books.columns = ["i1",'i2','ISBN', 'bookTitle', 'bookAuthor', 'yearOfPublication', 'publisher', 'imageUrlS', 'imageUrlM', 'imageUrlL','blurb']
users = pd.read_csv('BX-Users.csv', sep=';', error_bad_lines=False, encoding="latin-1")
users.columns = ['userID', 'Location', 'Age']
ratings = pd.read_csv('BX-Book-Ratings.csv', sep=';', error_bad_lines=False, encoding="latin-1")
ratings.columns = ['userID', 'ISBN', 'bookRating']

books.yearOfPublication=pd.to_numeric(books.yearOfPublication, errors='coerce')

books.loc[(books.yearOfPublication > 2006) | (books.yearOfPublication == 0),'yearOfPublication'] = np.NAN

books.yearOfPublication.fillna(round(books.yearOfPublication.mean()), inplace=True)

books.yearOfPublication = books.yearOfPublication.astype(np.int32)

books.loc[(books.ISBN == '193169656X'),'publisher'] = 'other'
books.loc[(books.ISBN == '1931696993'),'publisher'] = 'other'

users.loc[(users.Age > 90) | (users.Age < 5), 'Age'] = np.nan

users.Age = users.Age.fillna(users.Age.mean())

users.Age = users.Age.astype(np.int32)

n_users = users.shape[0]
n_books = books.shape[0]

ratings_new = ratings[ratings.ISBN.isin(books.ISBN)]

ratings_new = ratings_new[ratings_new.userID.isin(users.userID)]

#sparsity=1.0-len(ratings_new)/float(n_users*n_books)
#print('The sparsity level of Book Crossing dataset is ' +  str(sparsity*100) + ' %')

ratings_explicit = ratings_new[ratings_new.bookRating != 0]
ratings_implicit = ratings_new[ratings_new.bookRating == 0]

#import seaborn as sns
#sns.countplot(data=ratings_explicit , x='bookRating')
#plt.show()

ratings_count = pd.DataFrame(ratings_explicit.groupby(['ISBN'])['bookRating'].sum())
top10 = ratings_count.sort_values('bookRating', ascending = False).head(25)
#print("Following books are recommended")
topten = top10.merge(books, left_index = True, right_on = 'ISBN')

bookTitle = topten['bookTitle'].tolist() 
bookAuthor = topten['bookAuthor'].tolist() 
yop = topten['yearOfPublication'].tolist() 
image = topten['imageUrlS'].tolist() 

#books.to_excel("finalBooks.xlsx",sheet_name='Sheet_name_1')
#books.head(10)
"""
@app.route("/", methods=("POST", "GET"))
def home():
	if request.method=="POST":
		name=request.form.get("name")
		email=request.form.get("email")
		password=request.form.get("pass")
		int1=request.form.get("int1")
		int2=request.form.get("int2")
		interest=int1+","+int2
		cur=mysql.connection.cursor()
		cur.execute(
    """#INSERT INTO 
        #signup (
         #   name,
          #  email,
           # password,
            #interest_area)
  #  VALUES (%s,%s,%s,%s)""", (name, email, password,interest))
	#	mysql.connection.commit()
	#	cur.close()
#		return render_template('index.html',image=image,title=bookTitle,author=bookAuthor,yop=yop)
#	return render_template('index.html',image=image,title=bookTitle,author=bookAuthor,yop=yop)

#if __name__=="__main__":
#	app.run(debug=True)


@app.route("/", methods=("POST", "GET"))
def home():
     
         return render_template('index.html',image=image,title=bookTitle,author=bookAuthor,yop=yop)

@app.route("/signup",methods=("POST","GET"))
def signup():
    if request.method=="POST" and  "name" in request.form and "email" in request.form and "pass" in request.form and "int1" in request.form and "int2" in request.form:
    	name=request.form.get("name")
    	email=request.form.get("email")
    	password=request.form.get("pass")
    	int1=request.form.get("int1")
    	int2=request.form.get("int2")
    	interest=int1+","+int2
    	cur=mysql.connection.cursor()
    	cur.execute(
    """INSERT INTO 
        signup (
            name,
            email,
            password,
            interest_area)
    VALUES (%s,%s,%s,%s)""", (name, email, password,interest))
    	mysql.connection.commit()
    	cur.close()
    	return render_template('index.html',image=image,title=bookTitle,author=bookAuthor,yop=yop)
  
    elif request.method=="POST":      #if we dont fill signup form and submit/form is empty
        flash("Please fill the form!")
        redirect(url_for("signup"))
    return render_template('index.html',image=image,title=bookTitle,author=bookAuthor,yop=yop)

@app.route("/login",methods=("POST","GET"))
def login():
    if request.method=="POST" and "email" in request.form and "pswd" in request.form:#Check if "email" and password exist in database 
            email_id=request.form.get("email")
            password=request.form.get("pswd")    #check if account exist using mysql
            cursor=mysql.connection.cursor()
            cursor.execute('Select * FROM signup WHERE email = %s and password=%s',(email_id,password,))
            #fetch one record and return result
            account=cursor.fetchone()
            #if account exists in our databse signup then,
            if account:
                #create session data jisko hum kisi dusre route p access krskt
                session['loggedin'] =True
                session['name']=account[0]
                session['email']=account[1]
                session['interestarea']=account[1]
                flash("You are successfully logged in !!")
                return render_template('afterlogin.html',image=image,title=bookTitle,author=bookAuthor,yop=yop,name1=account[0],email1=account[1],interest1=account[3])   #this can be redirect anywhere else also u 
            else:
                flash("You are successfully logged in !!")
                return 'not ok'
    return render_template("index.html",image=image,title=bookTitle,author=bookAuthor,yop=yop)

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))             

                
if __name__=="__main__":
	app.secret_key = 'the random string'
	app.run(debug=True)	