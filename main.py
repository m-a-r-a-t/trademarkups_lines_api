import json
import os
import time

from flask import Flask, request



app = Flask(__name__)


@app.route("/all-extrems", methods=['GET'])
def get_all_extrems():
    return 'g'



if __name__ == "__main__":
    # app.run(host='95.182.120.52', port=8081)
    app.run(host='127.0.0.1', port=8081)
