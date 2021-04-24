import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import flask
from flask import abort, jsonify, request, redirect

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

if __name__ == '__main__':
    app.run(debug=False)