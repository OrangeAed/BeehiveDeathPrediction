import csv
from pymongo import MongoClient

from MongoUtils.mongo_helper import MongoHelper

def connect_to_client_remote():
    with open("auth.csv") as auth:
        csv_reader = csv.reader(auth, delimiter="\n")
        username = next(csv_reader)[0]
        password = next(csv_reader)[0]
        client = MongoHelper.connect_to_remote_client(username, password, "beeDB")

    return client

def connect_to_client_local():
    client = MongoClient("localhost", 27017)
    return client