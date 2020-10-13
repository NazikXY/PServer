from flask import Flask
from flask_restful import Resource, Api
from datetime import datetime
import sqlite3 as sq

app = Flask(__name__)
api = Api(app)
db = sq.connect('../V1/bot.db', check_same_thread=False)


class Server(Resource):
    def get(self):
        # return {'data': str(db.cursor().execute("SELECT * FROM goods").fetchall())}
        return {'data': "Podushechnaya Server"}

class GetCurrentOrder(Resource):
    def get(self):
        data = db.cursor().execute('SELECT * FROM "' + 'order_'+str(datetime.today().date())+'"').fetchall()
        return {'data': data}


api.add_resource(Server, '/')
api.add_resource(GetCurrentOrder, '/get_current_order/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='80')
