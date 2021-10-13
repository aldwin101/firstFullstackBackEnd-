from os import stat
import dbcreds
import mariadb
from flask import Flask, request, Response
import json
import sys

cursor = None
conn = None

app = Flask(__name__)

try:
    conn = mariadb.connect(user=dbcreds.user,
                        password=dbcreds.password,
                        host=dbcreds.host,
                        port=dbcreds.port,
                        database=dbcreds.database
                        )
    cursor = conn.cursor()

    @app.route("/api")
    def home():
        return "You can use a simple request for GET, POST, PATCH and DELETE using"

    @app.route('/api/posts', methods=['GET', 'POST', 'PATCH', 'DELETE'])

        # posts handler
    def posts():
        if request.method == 'GET':
            cursor.execute('SELECT * FROM posts')
            info = cursor.fetchall()
            infoData = []

            for user in info:
                userData = {
                    'userId' : user[0],
                    'content' : user[1]
                }
                infoData.append(userData)

            return Response(json.dumps(infoData),
                            mimetype="application/json",
                            status=200)

        if request.method == 'POST':
            data = request.json
            cursor.execute('INSERT INTO posts(content) VALUES (?)', 
                            [data.get('content')])
            conn.commit()
            return Response(json.dumps('Successfully uploaded a post'),
                            mimetype='application/json',
                            status=200)

        if request.method == 'PATCH':
            data = request.json
            cursor.execute('UPDATE posts SET content=?', 
                            [data.get('content')])
            conn.commit()
            return Response(json.dumps('Successfully edited the post'),
                            mimetype='application/json',
                            status=200)

        if request.method == 'DELETE':
            data = request.json
            cursor.execute("DELETE FROM posts WHERE id=?", [data.get('id')])
            conn.commit()
            return Response(json.dumps('Successfully deleted the post'),
                            mimetype='application/json',
                            status=200)
        
except mariadb.DataError:
    print("Something wrong with your data")
except mariadb.OperationalError:
    print("Something wrong with the connection")
except mariadb.ProgrammingError:
    print("Your query was wrong")
except mariadb.IntegrityError:
    print("Your query would have broken the database and we stopped it")
except:
    print("Something went wrong")
finally:
    if (cursor != None):
        cursor.close()
    else:
        print("There was never a cursor to begin with")
    if (conn != None):
        conn.rollback()
        conn.close()
    else:
        print("The connection never opened, nothing to close here")

if (len(sys.argv) > 1):
    mode = sys.argv[1]
    if (mode == "production"):
        import bjoern
        host = '0.0.0.0'
        port = 5000
        print("Server is running in production mode")
        bjoern.run(app, host, port)
    elif(mode == "testing"):
        from flask_cors import CORS
        CORS(app)
        print("Server is running in testing mode, switch to production when needed")
        app.run(debug=True) 
    else:
        print("Invalid mode argument, exiting")
        exit() 
else:
    print("No argument was provided")
    exit()