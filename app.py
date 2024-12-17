from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysql_connector import MySQL # Old version of Flask
# from flask_mysqldb import MySQL # Latest version Of Flask
import os

app=Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ictinfo'
app.secret_key = "hello"

UPLOAD_FOLDER = 'static/uploads' # Store uploaded images
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql=MySQL(app)

@app.route('/connect')
def connect():
    try:
        #create a cursor
        cur = mysql.connection.cursor()
        cur.execute("USE blog")
        # create a query
        query = "SELECT DATABASE()"
        #execute the query
        cur.execute(query)
        #fetch data
        db_name = cur.fetchone()
        return f"My database connected is : {db_name}"
    except Exception as e:
        return f"Error is : {e}"
    finally:
        cur.close()

@app.route("/")
def home():
    if "user" in session:
        return render_template("index.html")
    return render_template("login.html")

@app.route("/register",methods=["POST","GET"])
def register():
    if request.method=="POST":
        name=request.form['txt']
        mobile=request.form['mobile']
        pswd=request.form['pswd']
        print(name,mobile,pswd)
        try:
            cur = mysql.connection.cursor()
            cur.execute("USE blog")
            cur.execute("INSERT INTO user(name,mobile,password) VALUES (%s,%s,%s)",(name,mobile,pswd))
            mysql.connection.commit()
            return redirect(url_for("home"))
        except Exception as e:
            return f"Exception thrown is: {e}"
        finally:
            cur.close()

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method=="POST":
        mobile=request.form['mobile']
        pswd=request.form['pswd']
        print(mobile,pswd)
        try:
            cur = mysql.connection.cursor()
            cur.execute("USE blog")
            # Check if user already exists based on name or mobile
            cur.execute("SELECT * FROM user WHERE mobile = %s AND password = %s", (mobile, pswd))
            existing_user = cur.fetchall()
            print(existing_user)
            
            if existing_user and len(existing_user)==1:
                session['user'] = mobile
                session['name'] = existing_user[0][1]
                return render_template("index.html")
        
            return redirect(url_for("home"))
        except Exception as e:
            return f"Exception thrown is: {e}"
        finally:
            cur.close()  # Ensure cursor is closed properly

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/blog")
def blog():
    try:
        cur = mysql.connection.cursor()
        cur.execute("USE blog")
        cur.execute("SELECT * FROM blogs")
        blog_data = cur.fetchall()
        print("Blogs Data:",blog_data)
        return render_template("blog.html", blogs=blog_data)
    except Exception as e:
        return f"An error occurred: {e}"    
    finally:
        cur.close()
    

@app.route("/single")
def single():
    return render_template("single.html")

@app.route("/signout")
def signout():
    session.clear()
    return render_template("login.html")

@app.route("/addblog")
def addblog():
    return render_template("addblog.html")

@app.route("/post", methods=["POST", "GET"])
def post():
    if request.method=="POST":
        title=request.form['title']
        category=request.form['category']
        blog=request.form['content']
        print("Got Values",title,category,blog)
        print(request.files)
        # Check if an image file is uploaded
        if 'image' in request.files:
            print("file")
            file = request.files['image']
            fname = file.filename
            fpath = os.path.join(app.config['UPLOAD_FOLDER'], fname)
            file.save(fpath)

            try:
                print("add")
                cur = mysql.connection.cursor()
                cur.execute("USE blog")
                cur.execute("INSERT INTO blogs(title,category,blog,image) VALUES (%s,%s,%s,%s)",(title,category,blog,fpath))
                mysql.connection.commit()
                return redirect(url_for("blog"))
            except Exception as e:
                return f"Exception thrown is: {e}"
            finally:
                cur.close()
    return render_template("addblog.html")

if __name__=="__main__":
    app.run(debug=True)