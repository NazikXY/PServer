from flask import Flask
from flask_restful import Resource, Api
from datetime import datetime
import json
import sqlite3 as sq

app = Flask(__name__)
api = Api(app)
db = sq.connect('../PBot/bot.db', check_same_thread=False)


class Server(Resource):
    def get(self):
        # return {'data': str(db.cursor().execute("SELECT * FROM goods").fetchall())}
        return {'data': "Podushechnaya API"}


class GetCurrentOrder(Resource):
    def get(self):
        today = 'order_'+str(datetime.today().date())
        data = db.cursor().execute('SELECT goods.name, "' + today +
                                   '".count FROM goods JOIN "' + today +
                                   '" ON goods.gid == "' + today + '".goods_id').fetchall()
        return {'data': data}


class GetOrdersSequence(Resource):
    def get(self):
        data = db.cursor().execute('SELECT * FROM history').fetchall()
        goods = db.cursor().execute('SELECT gid, name, units FROM goods').fetchall()
        goods_dict = dict()
        # print(data)
        for i in goods:
            goods_dict[str(i[0])] = {str(i[1]), str(i[2])}
        new_data = []
        # print(goods_dict)
        a = json.loads(data[0][2])

        for i in a:
            new_data.append([goods_dict[str(i[0])], i[1]])
        data = {"id": data[0][0], "name":data[0][1], "orders_list": new_data}

        return {'data': data}


api.add_resource(Server, '/')
api.add_resource(GetCurrentOrder, '/get_current_order/')
api.add_resource(GetOrdersSequence, '/get_orders_sequence')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='80')

