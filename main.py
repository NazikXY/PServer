from json.decoder import JSONDecodeError
from pprint import pprint

from flask import Flask
from flask_restful import Resource, Api, reqparse
from pandas import DataFrame
from datetime import datetime
import json
import sqlite3 as sq

app = Flask(__name__)
api = Api(app)
db = sq.connect('storage.db', check_same_thread=False)
parser = reqparse.RequestParser()
parser.add_argument('data')



class Server(Resource):
    def get(self):
        # return {'data': str(db.cursor().execute("SELECT * FROM goods").fetchall())}
        return {'data': "Podushechnaya API"}


class GetUser(Resource):
    def get(self):
        db_users = db.cursor().execute('SELECT * FROM "users"').fetchall()
        result = []
        for i in db_users:
            tmp_dict = dict()
            tmp_dict['id'] = i[0]
            tmp_dict['name'] = i[1]
            tmp_dict['email'] = i[2]
            tmp_dict['phone'] = i[3]
            tmp_dict['role'] = i[4]
            tmp_dict['hashcode'] = i[5]
            result.append(tmp_dict)

        return result

# TODO make it safe


class GetProducts(Resource):
    def get(self):
        _parser = reqparse.RequestParser()
        _parser.add_argument('id')
        cid = _parser.parse_args()['id']
        req_str = 'SELECT * FROM "products"' + (f' WHERE "category" == {cid}' if cid is not None else "")
        db_products = db.cursor().execute(req_str).fetchall()
        result = []
        for i in db_products:
            tmp_dict = dict()
            tmp_dict['id'] = i[0]
            tmp_dict['name'] = i[1]
            tmp_dict['units'] = i[2]
            tmp_dict['category'] = i[3]
            tmp_dict['imageURI'] = i[4]
            result.append(tmp_dict)

        return result


class GetCategories(Resource):
    def get(self):
        db_categories = db.cursor().execute('SELECT * FROM "categories"').fetchall()
        result = []
        for i in db_categories:
            tmp_dict = dict()
            tmp_dict['id'] = i[0]
            tmp_dict['name'] = i[1]
            tmp_dict['imageURI'] = i[2]
            db_products = db.cursor().execute(f'SELECT * FROM "products" WHERE "category" == {i[0]}').fetchall()
            resulti = []
            for a in db_products:
                tmp_dicti = dict()
                tmp_dicti['id'] = a[0]
                tmp_dicti['name'] = a[1]
                tmp_dicti['units'] = a[2]
                tmp_dicti['category'] = a[3]
                tmp_dicti['imageURI'] = a[4]
                resulti.append(tmp_dicti)
            tmp_dict['productList'] = resulti
            result.append(tmp_dict)

        return result


class GetPlaces(Resource):
    def get(self):
        db_products = db.cursor().execute('SELECT * FROM "places"').fetchall()
        result = []
        for i in db_products:
            tmp_dict = dict()
            tmp_dict['id'] = i[0]
            tmp_dict['name'] = i[1]
            result.append(tmp_dict)
        return result


class GetRoles(Resource):
    def get(self):
        db_products = db.cursor().execute('SELECT * FROM "roles"').fetchall()
        result = []
        for i in db_products:
            tmp_dict = dict()
            tmp_dict['id'] = i[0]
            tmp_dict['name'] = i[1]
            result.append(tmp_dict)
        return result


class GetOrders(Resource):
    def get(self):
        args = parser.parse_args()

        db_user_orders = db.cursor().execute(f'SELECT * FROM "orders" WHERE "target" == "{args["data"]}"').fetchall()

        full_product_list = []

        for order in db_user_orders:
            products_string = order[3]
            products_list = json.loads(products_string.replace("'", '"'))
            # , 'product': json.loads(((data_products.loc[item['id']]).to_json()))}
            full_product_list.append([{'count': item['count'], 'id': item['id'] }for item in products_list])
        dicts_list = [{'id': item[0], 'name': item[1], 'place': item[2],
                       'miniPositionList': full_product_list[index],
                       'comment': item[5]} for index, item in enumerate(db_user_orders)]
        return dicts_list

    def post(self):
        arg = parser.parse_args()
        data = json.loads(arg.get('data'))
        id = data
        print(data)
        db_orders = db.cursor().execute('SELECT * FROM "orders" WHERE "target" == "{}"'.format(data)).fetchall()
        result = []
        for i in db_orders:
            tmp_dict = dict()
            tmp_dict['id'] = i[0]
            tmp_dict['name'] = i[1]
            tmp_dict['place'] = i[2]
            tmp_dict['order'] = i[3]
            # tmp_dict['target'] = i[4]
            result.append(tmp_dict)
        return result


class RegUser(Resource):
    def post(self):
        arg = parser.parse_args()
        data = json.loads(arg.get('data'))

        db.cursor().execute('INSERT INTO "users" (name, "e-mail", phone, role, hashcode) VALUES ("{}", "{}","{}","{}", "{}")'.format(data['name'], data['email'], data['tel'], data['role'], data['hash']))
        db.commit()
        user_id = db.cursor().execute('SELECT "id" FROM "users" WHERE "e-mail" == "{}"'.format(data['email'])).fetchone()[0]
        return {'data': user_id}

class SendOrder(Resource):
    def post(self):
        arg = parser.parse_args()
        data = json.loads(arg.get('data').replace("'", '"'))
        # jorder = json.dumps(data['order'])
        db.cursor().execute('INSERT INTO "orders" ("name", "place", "order", "target", "comment") VALUES ("{}", "{}", "{}", "{}", "{}")'.format(data['name'], data['place'], data['order'], data['target'], data['comment']))
        db.commit()
        return 1

class SignIn(Resource):
    def post(selt):
        arg = parser.parse_args()
        print(arg)
        data = json.loads(str(arg.get('data').replace("'", '"')))
        result = "FAILED"

        if data['email']:
            req = f'''
            SELECT password, "e-mail" FROM "users" INNER JOIN pwds ON user_id == "users"."id" WHERE "e-mail" == "{data['email']}"
            '''
            usr = db.cursor().execute(req).fetchone()

            if data['password'] == usr[0]:
                print('Success')
                result = db.cursor().execute(f'SELECT * FROM users WHERE "e-mail" == "{data["email"]}"').fetchone()
                print(result)


        if data['tel']:
            req = f'''
            SELECT password, "phone" FROM "users" INNER JOIN pwds ON user_id == "users"."id" WHERE "phone" == "{data['tel']}"
            '''
            usr = db.cursor().execute(req).fetchone()
            if data['password'] == usr[0]:
                print('Success')
                result = db.cursor().execute(f'SELECT * FROM users WHERE "phone" == "{data["tel"]}"').fetchone()
                print(result)

        return {'id': result[0], 'user_name': result[1], 'email': result[2], "phone": result[3],
                "role": result[4]}




api.add_resource(Server, '/')
# api.add_resource(GetOrdersSequence, '/get_orders_sequence')
api.add_resource(GetUser,       '/get_all_users/')
api.add_resource(GetProducts,   '/get_all_products/')
api.add_resource(GetCategories, '/get_categories')
api.add_resource(GetPlaces,     '/get_places')
api.add_resource(GetRoles,      '/get_roles')
api.add_resource(GetOrders,     '/get_orders')
api.add_resource(RegUser, '/reg')
api.add_resource(SendOrder, '/send_order')
api.add_resource(SignIn, '/sign_in')



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='80')

