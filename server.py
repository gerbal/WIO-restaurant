from flask import Flask, request, render_template, make_response, url_for, redirect
from flask.ext.restful import Api, Resource, reqparse, abort

import json
import string
import random
from datetime import datetime
import rdflib

schema = rdflib.Namespace("http://schema.org/")

# define our priority levels
PRIORITIES = ( 'closed', 'low', 'normal', 'high' )

# load help requests data from disk
with open('data.json') as data:
    data = json.load(data)

#
# define some helper functions
#
def generate_id(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def error_if_menu_not_found(menu_id):
    if menu_id not in data.keys():
        message = "Menu {} doesn't exist".format(menu_id)
        abort(404, message=message)

def error_if_dish_not_found(menu_id, dish_id):
    if menu_id not in data.keys():
        message = "Menu {} doesn't exist".format(menu_id)
        abort(404, message=message)
    elif dish_id not in data[menu_id]["dishes"]:
        message = "Dish {} doesn't exist".format(dish_id)
        abort(404, message=message)

def filter_and_sort_helprequests(q='', sort_by='time'):
    filter_function = lambda x: q.lower() in (
        x[1]['title'] + x[1]['description']).lower()
    filtered_helprequests = filter(filter_function,
                                   data["helprequests"].items())
    key_function = lambda x: x[1][sort_by]
    return sorted(filtered_helprequests, key=key_function, reverse=True)


def filter_dict_list(dic):
    keys = dic.keys()
    keylist = lambda x: dic[x]
    return_list = map(keylist, keys)
    return return_list


def render_menu_list_as_html(menus):
    return render_template(
        'menus_list.html',
        menus= menus)

def render_menu_as_html(menu, menu_id):
    return render_template(
        'menu.html',
        menu= menu, menu_id=menu_id)

def render_dish_as_html(dish):
    return render_template(
        'dish.html',
        dish=dish)# filter_dict_list(dish))

def nonempty_string(x):
    s = str(x)
    if len(x) == 0:
        raise ValueError('string is empty')
    return s

#
# specify the data we need to create a new help request
#

new_menu_parser = reqparse.RequestParser()
for arg in ['menu_title','menu_description']:
    new_menu_parser.add_argument(
        arg, type=nonempty_string, required=True,
        help="'{}' is a required value".format(arg))

new_dish_parser = reqparse.RequestParser()
for arg in ['item_name','dish_description']:
    new_dish_parser.add_argument(
        arg, type=nonempty_string, required=True,
        help="'{}' is a required value".format(arg))

#
# specify the data we need to update an existing help request
#
update_dish_parser = reqparse.RequestParser()
update_dish_parser.add_argument(
    'ingredient', type=str, default='')
update_dish_parser.add_argument(
    'description', type=str, default='')
update_dish_parser.add_argument(
    'del-ingredient', type=str, default='')

#
# specify the parameters for filtering and sorting help requests
#
query_parser = reqparse.RequestParser()
query_parser.add_argument(
    'q', type=str, default='')
query_parser.add_argument(
    'sort-by', type=str, choices=('priority', 'time'), default='time')

#
# define our (kinds of) resources
#

class getMenu(Resource):
    def get(self, menu_id):
        error_if_menu_not_found(menu_id)
        #error_if_helprequest_not_found(helprequest_id)
        return make_response(
            render_menu_as_html(
                data[menu_id], menu_id), 200)

    def put(self, menu_id):
        error_if_menu_not_found(menu_id)
        update = new_dish_parser.parse_args()
        print update
        new_dish = 'dish-'+generate_id()
        data[menu_id]['dishes'][new_dish] = {"dish": update['item_name'],
                                             'dish_description': update['dish_description'],
                                             'ingredient_list': {}}

        menu = data[menu_id]
        return make_response(
            render_menu_as_html(menu, menu_id), 200)
    def delete(self, menu_id):
        error_if_menu_not_found(menu_id)
        menu = data[menu_id]
        del data[menu_id]
        return make_response(
            render_dish_as_html(menu, menu_id), 204)


class menuList(Resource):
    def get(self):
        return make_response(
            render_menu_list_as_html(data),  200)

    def post(self):
        update = new_menu_parser.parse_args()
        new_menu_id = 'menu-'+generate_id()
        data[new_menu_id] = {
            'menu': update['menu_title'],
            'description': update['menu_description'],
            'dishes':{}}
        return make_response(
            render_menu_list_as_html(data), 201)

# class HelpRequestListAsJSON(Resource):
#     def get(self):
#         return data

class getDish(Resource):
    def get(self, menu_id, dish_id):
        error_if_dish_not_found(menu_id, dish_id)
	dish = data[menu_id]['dishes'][dish_id]
	ingredients = dish['ingredient_list'].values()
	for i in ingredients:
            graph = rdflib.Graph()
	    graph.parse("http://aeshin.org:6789/produces?q={}".format(i['ingredient']))
            i['links'] = []
	    for s, o in graph.subject_objects(predicate=schema.name):
	        i['links'].append({ 'text': str(o), 'href': str(s) })
        print(dish)
	return make_response(
            render_dish_as_html(dish)
                , 200)
    def patch(self, menu_id, dish_id):
        error_if_dish_not_found(menu_id, dish_id)
        update = update_dish_parser.parse_args()
        # print update
        if len(update['ingredient']) > 0:
            new_ingredient = 'ingredient-'+generate_id()
            data[menu_id]['dishes'][dish_id]['ingredient_list'][new_ingredient] = {
                'ingredient_description': update['description'],
                'ingredient': update['ingredient']}
            # dish = data[menu_id]['dishes'][dish_id]
        elif len(update['del-ingredient']) > 0:
            # dish = data[menu_id]['dishes'][dish_id]
            match = ""
            for i in data[menu_id]['dishes'][dish_id]['ingredient_list']:
                if data[menu_id]['dishes'][dish_id]['ingredient_list'][i]['ingredient'] == update['del-ingredient']:
                    match = i
            del data[menu_id]['dishes'][dish_id]['ingredient_list'][match]

        dish = data[menu_id]['dishes'][dish_id]
        print update
        return make_response(
            render_dish_as_html(dish), 200)
    def delete(self, menu_id, dish_id):
        error_if_dish_not_found(menu_id, dish_id)
        dish = data[menu_id]['dishes'][dish_id]
        del data[menu_id]['dishes'][dish_id]
        return make_response(
            render_dish_as_html(dish), 204)
#
# assign URL paths to our resources
#
app = Flask(__name__)
api = Api(app)
api.add_resource(menuList, '/list_of_menus')
#api.add_resource(HelpRequestListAsJSON, '/requests.json')
api.add_resource(getMenu, '/menu/<string:menu_id>/')
api.add_resource(getDish, '/menu/<string:menu_id>/<string:dish_id>')
#api.add_resource(HelpRequestAsJSON, '/request/<string:helprequest_id>.json')

# start the se
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5555)





