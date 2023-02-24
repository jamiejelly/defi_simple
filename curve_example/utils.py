import json
import os
import pickle
import requests
import time
from urllib.parse import urlencode

from datetime import datetime


def make_endpoint(endpoint, **args):
    return endpoint + '?' + urlencode(args) if args else endpoint


def make_get_request(url, endpoint, **args):
    return requests.get(os.path.join(url, make_endpoint(endpoint, **args))).json()


def get_timestamp_ms(): # in milliseconds
    return int(round(time.time() * 1000))


def convert_dt_to_ms(year, month, day):
    return int(datetime(year, month, day).timestamp() * 1000)


def convert_ms_to_dt(x):
    return datetime.fromtimestamp(int(x/1000))


def load_config(name="config.ini"):
    from configparser import ConfigParser
    config = ConfigParser()
    config.read(name)
    return config


# def write_to_json(dct, filename):
#     with open(f'{filename}.json', 'w') as f:
#         json.dump(dct, f)


# def read_from_json(filename):
#     with open(f'{filename}.json') as f:
#         data = json.load(f)
#     return data


# def write_to_pickle(obj, f):
#     with open(f, "wb") as f:
#         pickle.dump(obj, f)


# def read_from_pickle(f):
#     with open(f, "rb") as f:
#         obj = pickle.load(f)
#     return obj