import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import flask
from flask import abort, jsonify, request, redirect

from math import sin, cos, sqrt, atan2, radians

import datetime
import json
import requests

# Initiating Flask App
app = flask.Flask(__name__)

cred = credentials.Certificate("dubbed-zomato-7a6ca-firebase-admin-key.json")
firebase_app = firebase_admin.initialize_app(cred)
store = firestore.client()

@app.route('/add_restaurant', methods=['POST'])
def add_restaurant():
    data = request.get_json(force=True)
    dikt = {}
    dikt["name"] = data.get("name")
    dikt["mobile_number"] = data.get("mobile_number")
    dikt["address"] = data.get("address")
    dikt["location"] = {
        "latitude" : data.get("latitude"),
         "longitude" : data.get("longitude")
         }
    dikt["type"] = data.get("typ")
    dikt["image"] = data.get("img")
    dikt["restaurant_id"] = data.get("restaurant_id")
    dikt["restaurant_created_at"] = firestore.SERVER_TIMESTAMP

    store.collection("RESTAURANTS").add(dikt)
    return jsonify({"Response" : 200})


@app.route('/search_restaurant/by_id', methods=['POST'])
def search_restaurant():
    data = request.get_json(force=True)
    restaurant_id = data.get("restaurant_id")
    arr = store.collection("RESTAURANTS").where("restaurant_id","==",restaurant_id).stream()
    restaurants_list = []
    for val in arr:
        restaurants_list.append(val.to_dict())
    return jsonify({"Response" : 200, "Restaurants_list" : restaurants_list})

@app.route('/search_restaurant/by_coordinates', methods=['POST'])
def search_restaurant_by_coordinates():
    data = request.get_json(force=True)
    mylat = data.get("latitude")
    mylon = data.get("longitude")
    r = data.get("range")

    # approximate radius of earth in km
    R = 6373.0

    arr = store.collection("RESTAURANTS").stream()
    restaurants_near_me = []
    for restaurant in arr:
        try:
            rdict = restaurant.to_dict()
            rlat = rdict.get("location").get("latitude")
            rlon = rdict.get("location").get("longitude")

            mylat = radians(mylat)
            mylon = radians(mylon)
            rlat = radians(rlat)
            rlon = radians(rlon)

            dlon = rlon - mylon
            dlat = rlat - mylat

            a = sin(dlat / 2)**2 + cos(mylat) * cos(rlat) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distance = R * c

            if(distance<=r):
                restaurants_near_me.append(rdict)
        except Exception as e:
            print(e)
    return jsonify({"Response" : 200, "Restaurants_near_me" : restaurants_near_me})

@app.route('/create_menu', methods=['POST'])
def create_menu():
    data = request.get_json(force=True)
    dikt = {}
    dikt["menu_id"] = data.get("menu_id")
    dikt["restaurant_id"] = data.get("restaurant_id")
    dikt["menu_items"] = data.get("menu_items")
    dikt["menu_created_at"] = firestore.SERVER_TIMESTAMP

    store.collection("MENUS").add(dikt)
    return jsonify({"Response" : 200})

@app.route('/add_item', methods=['POST'])
def add_item_to_menu():
    data = request.get_json(force=True)
    menu_id = data.get("menu_id")
    menu_item = data.get("menu_item")

    restaurant = list(store.collection("MENUS").where("menu_id","==",menu_id).stream())
    ref = store.collection("MENUS").document(restaurant[0].id)
    ref.update({u'menu_items': firestore.ArrayUnion([menu_item])})
    return jsonify({"Response" : 200})

if __name__ == '__main__':
    app.run(debug=False)