import json
import os
import time
from db import Database as DB
from flask import Flask, request


app = Flask(__name__)


@app.route("/charts", methods=['GET'])
def get_all_charts_by_pair():
    db = DB()
    try:
        pair = request.args.get('pair').upper()
    except:
        pair = None
    print(pair)
    chart_name = request.args.get('chart_name')

    if chart_name is not None and pair is not None:
        try:
            lines = db.get_lines_by_chart_name_and_pair(pair,chart_name)
            return lines
        except:
            return {'Error' : 'Chart with this name does not exist !'}
    elif pair is not None:
        charts_names = db.get_charts_by_pair(pair)
        print(charts_names)
        return  json.dumps(charts_names)
    else:
        return json.dumps({'Error' :'Need pair param'})



if __name__ == "__main__":
    app.run(host='95.182.120.52', port=8085)
    # app.run(host='127.0.0.1', port=8085)
