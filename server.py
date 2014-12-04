from flask import Flask, request, render_template, make_response
from flask.ext.restful import Api, Resource, reqparse, abort

import json
import string
import random
from datetime import datetime

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

def filter_and_sort_helprequests(q='', sort_by='time'):
    filter_function = lambda x: q.lower() in (
        x[1]['title'] + x[1]['description']).lower()
    filtered_helprequests = filter(filter_function,
                                   data["helprequests"].items())
    key_function = lambda x: x[1][sort_by]
    return sorted(filtered_helprequests, key=key_function, reverse=True)

def render_helprequest_as_html(helprequest):
    return render_template(
        'helprequest+microdata+rdfa.html',
        helprequest=helprequest,
        priorities=reversed(list(enumerate(PRIORITIES))))

def filter_dict_list(dic):
    keys = dic.keys()
    keylist = lambda x: dic[x]
    return_list = map(keylist, keys)
    return return_list


def render_menu_list_as_html(menus):
    return render_template(
        'menus_list.html',
        menus= filter_dict_list(menus))

def render_menu_as_html(menu):
    return render_template(
        'menu.html',
        menu= filter_dict_list(menu))

def render_dish_as_html(dish):
    return render_template(
        'dishes.html',
        dish=dish)# filter_dict_list(dish))

def nonempty_string(x):
    s = str(x)
    if len(x) == 0:
        raise ValueError('string is empty')
    return s

#
# specify the data we need to create a new help request
#
new_helprequest_parser = reqparse.RequestParser()
for arg in ['from', 'title', 'description']:
    new_helprequest_parser.add_argument(
        arg, type=nonempty_string, required=True,
        help="'{}' is a required value".format(arg))

#
# specify the data we need to update an existing help request
#
update_helprequest_parser = reqparse.RequestParser()
update_helprequest_parser.add_argument(
    'priority', type=int, default=PRIORITIES.index('normal'))
update_helprequest_parser.add_argument(
    'comment', type=str, default='')

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
# class helprequest(Resource):
#     def get(self, helprequest_id):
#         error_if_helprequest_not_found(helprequest_id)
#         return make_response(
#             render_helprequest_as_html(
#                 data["helprequests"][helprequest_id]), 200)
#
#     def patch(self, helprequest_id):
#         error_if_helprequest_not_found(helprequest_id)
#         helprequest = data["helprequests"][helprequest_id]
#         update = update_helprequest_parser.parse_args()
#         helprequest['priority'] = update['priority']
#         if len(update['comment'].strip()) > 0:
#             helprequest.setdefault('comments', []).append(update['comment'])
#         return make_response(
#             render_helprequest_as_html(helprequest), 200)

class getMenu(Resource):
    def get(self, menu_id):
        #error_if_helprequest_not_found(helprequest_id)
        return make_response(
            render_menu_as_html(
                data[menu_id]), 200)

    def patch(self, menu_id):
        error_if_menu_not_found(menu_id)
        helprequest = data["helprequests"][menu_id]
        update = update_helprequest_parser.parse_args()
        helprequest['priority'] = update['priority']
        if len(update['comment'].strip()) > 0:
            helprequest.setdefault('comments', []).append(update['comment'])
        return make_response(
            render_helprequest_as_html(helprequest), 200)

# class HelpRequestAsJSON(Resource):
#     def get(self, helprequest_id):
#         error_if_helprequest_not_found(helprequest_id)
#         helprequest = data["helprequests"][helprequest_id]
#         helprequest["@context"] = data["@context"]
#         return helprequest
#
# class HelpRequestList(Resource):
#     def get(self):
#         query = query_parser.parse_args()
#         return make_response(
#             render_helprequest_list_as_html(
#                 filter_and_sort_helprequests(
#                     q=query['q'], sort_by=query['sort-by'])), 200)
#
#     def post(self):
#         helprequest = new_helprequest_parser.parse_args()
#         helprequest['time'] = datetime.isoformat(datetime.now())
#         helprequest['priority'] = PRIORITIES.index('normal')
#         helprequests[generate_id()] = helprequest
#         return make_response(
#             render_helprequest_list_as_html(
#                 filter_and_sort_helprequests()), 201)

class menuList(Resource):
    def get(self):
        return make_response(
            render_menu_list_as_html(
                #filter_and_sort_helprequests(
                #q=query['q'], sort_by=query['sort-by'])),
                   data),  200)

    def post(self):
        helprequest = new_helprequest_parser.parse_args()
        helprequest['time'] = datetime.isoformat(datetime.now())
        helprequest['priority'] = PRIORITIES.index('normal')
        helprequests[generate_id()] = helprequest
        return make_response(
            render_helprequest_list_as_html(
                filter_and_sort_helprequests()), 201)

# class HelpRequestListAsJSON(Resource):
#     def get(self):
#         return data

class getDish(Resource):
    def get(self, menu_id, dish_id):
        return make_response(
            render_dish_as_html(data[menu_id]['dishes'][dish_id])
                , 200)
    # def patch(self, menu_id, dish_id):
    #     error_if_dish_not_found(menu_id, dish_id)
    #     dish = data[menu_id]['dishes'][dish_id
    #     update = update_helprequest_parser.parse_args()
    #     helprequest['priority'] = update['priority']
    #     if len(update['comment'].strip()) > 0:
    #         helprequest.setdefault('comments', []).append(update['comment'])
    #     return make_response(
    #         render_helprequest_as_html(helprequest), 200)
#
# assign URL paths to our resources
#
app = Flask(__name__)
api = Api(app)
api.add_resource(menuList, '/list_of_menus')
#api.add_resource(HelpRequestListAsJSON, '/requests.json')
api.add_resource(getMenu, '/menu/<string:menu_id>')
api.add_resource(getDish, '/dish/<string:menu_id>/<string:dish_id>')
#api.add_resource(HelpRequestAsJSON, '/request/<string:helprequest_id>.json')

# start the se
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5555)





