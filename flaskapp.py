
from flask import Flask, request, g, render_template, send_file

DATABASE = '/var/www/html/flaskapp/example.db'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_to_database():
    return sqlite3.connect(app.config['DATABASE'])

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def execute_query(query, args=()):
    cur = get_db().execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows

def commit():
    get_db().commit()

@app.route("/")
def hello():
    execute_query("DROP TABLE IF EXISTS users")
    execute_query("CREATE TABLE users (Username text,Password text,firstname text, lastname text, email text, count integer)")
    return render_template('index.html')

@app.route('/login', methods =['POST', 'GET'])
def login():
    message = ''
    if request.method == 'POST' and str(request.form['username']) !="" and str(request.form['password']) != "":
        username = str(request.form['username'])
        password = str(request.form['password'])
        result = execute_query("""SELECT firstname,lastname,email,count  FROM users WHERE Username  = (?) AND Password = (?)""", (username, password ))
        if result:
            for row in result:
                return responsePage(row[0], row[1], row[2], row[3])
        else:
            message = 'Invalid Credentials !'
    elif request.method == 'POST':
        message = 'Please enter Credentials'
    return render_template('index.html', message = message)

@app.route('/registration', methods =['GET', 'POST'])
def registration():
    message = ''
    if request.method == 'POST' and str(request.form['username']) !="" and str(request.form['password']) !="" and str(request.form['firstname']) !="" and str(request.form['lastname']) !="" and str(request.form['email']) !="":
        username = str(request.form['username'])
        password = str(request.form['password'])
        firstname = str(request.form['firstname'])
        lastname = str(request.form['lastname'])
        email = str(request.form['email'])
        uploaded_file = request.files['textfile']
        if not uploaded_file:
            filename = null
            word_count = null
        else :
            filename = uploaded_file.filename
            word_count = getNumberOfWords(uploaded_file)
        result = execute_query("""SELECT *  FROM users WHERE Username  = (?)""", (username, ))
        if result:
            message = 'User has already registered!'
        else:
            result1 = execute_query("""INSERT INTO users (username, password, firstname, lastname, email, count) values (?, ?, ?, ?, ?, ? )""", (username, password, firstname, lastname, email, word_count, ))
            commit()
            result2 = execute_query("""SELECT firstname,lastname,email,count  FROM users WHERE Username  = (?) AND Password = (?)""", (username, password ))
            if result2:
                for row in result2:
                    return responsePage(row[0], row[1], row[2], row[3])
    elif request.method == 'POST':
        message = 'Some of the fields are missing!'
    return render_template('registration.html', message = message)

@app.route("/download")
def download():
    path = "Limerick.txt"
    return send_file(path, as_attachment=True)

def getNumberOfWords(file):
    data = file.read()
    words = data.split()
    return str(len(words))

def responsePage(firstname, lastname, email, count):
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                text-align: center;
            }

            h1 {
                font-size: 36px;
                color: #555;
                margin-bottom: 20px;
            }

            .data-container {
                display: inline-block;
                background-color: #f2f2f2;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 0px 10px #ccc;
                text-align: left;
                width: 500px;
            }

            .data-item {
                font-size: 18px;
                margin: 20px 0;
            }

            .download-link {
                background-color: #333;
                color: #fff;
                padding: 10px 20px;
                border-radius: 20px;
                text-decoration: none;
                box-shadow: 0px 0px 10px #000;
                margin-top: 20px;
                display: inline-block;
            }

            .download-link:hover {
                background-color: #fff;
                color: #333;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <h1>Response Page</h1>
        <div class="data-container">
            <div class="data-item">First Name: <b>""" + str(firstname) + """</b></div>
            <div class="data-item">Last Name: <b>""" + str(lastname) + """</b></div>
            <div class="data-item">Email: <b>""" + str(email) + """</b></div>
           <div class="data-item">Word Count: <b>""" + str(count) + """</b></div>
         <a href="/download" class="download-link">Download</a>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
  app.run()