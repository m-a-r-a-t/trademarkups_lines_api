import psycopg2
import os
import re
import json
from psycopg2.extras import DictCursor, RealDictCursor
from dotenv import load_dotenv
dotenv_path = os.path.join('config/.env')


class Database:
    def __init__(self, logs=''):
        self.logs = logs
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
            self.conn = psycopg2.connect(dbname=os.getenv('DB_NAME'), user=os.getenv('USER_NAME'),
                                         password=os.getenv('PASSWORD'), host=os.getenv('HOST'))
        else:
            print('Failed connection to db')
            exit()

        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)

    def get_charts_by_pair(self, pair):

        self.cursor.execute(
            'SELECT name FROM "Charts" WHERE "symbol" = %s ;', (pair,)
        )
        return [dict(i) for i in self.cursor.fetchall()]

    def get_lines_by_chart_name_and_pair(self , pair ,chart_name):
        lines = []
        log = False
        self.cursor.execute(
            'SELECT * FROM "Charts" WHERE "symbol" = %s  and "name" = %s ;', (pair,chart_name)
        )
        chart = self.cursor.fetchall()[0]
        shapes = json.loads(json.loads(chart['content'])['content'])[
                'charts'][0]['panes'][0]['sources']
        for shape in shapes:
                if 'priceAxisProperties' in shape['state']:
                    log = shape['state']['priceAxisProperties']['log']
                if 'text' in shape['state'].keys():
                    data = {"text": shape['state']['text'], "points": shape["points"],'lineStyle':{
                        'color':shape['state']['linecolor'],
                        'style':shape['state']['linestyle'],
                        'width':shape['state']['linewidth']
                        }}
                    lines.append(data)

        

        return {'pair':pair,'chart_name':chart_name,'lines':lines,'log':log,'timeframe':json.loads(chart['content'])['resolution']}

    def __getMarkupsFromDB(self):
        self.cursor.execute(
            'SELECT * FROM "Charts" WHERE "isSignal" = true  ;')
        markups = self.cursor.fetchall()
        self.cursor.close()
        self.conn.close()
        # print(markups)
        return markups

    def __parseAndGetMarkupLines(self, markups):
        parsedMarkups = []

        for markup in markups:
            shapes = json.loads(json.loads(markup['content'])['content'])[
                'charts'][0]['panes'][0]['sources']
            log = None
            lines = []
            for shape in shapes:
                if 'priceAxisProperties' in shape['state']:
                    log = shape['state']['priceAxisProperties']['log']
                if 'text' in shape['state'].keys() and re.search("line", shape['state']['text'], flags=re.IGNORECASE):
                    lines.append(
                        {"lineType": shape['state']['text'], "points": shape["points"]})
            parsedMarkups.append({
                "log": log,
                "lines": lines,
                "name": markup['name'],
                "symbol": markup['symbol'],
                "resolution": markup['resolution'],
                "exchange": json.loads(markup['content'])['exchange']
            })
        return parsedMarkups

    def getParsedMarkup(self):
        new_markup = []
        parsed_markup = self.__parseAndGetMarkupLines(self.__getMarkupsFromDB())
        for i in range(len(parsed_markup)):
            # ! high low timestamp
            try:
                h_l_t = self.candles.get_candles(parsed_markup[i]['symbol'], parsed_markup[i]['exchange'], parsed_markup[i]['resolution'])
                parsed_markup[i]['candle_data'] = h_l_t
                if h_l_t == 'bad':
                    continue
                new_markup.append(MathOperaions.calcPointCoordsOfTheLines(parsed_markup[i]))
            except Exception as e:
                print(e)
                self.logs.write('Ошибка в расчетах')
        #! 'candle_data': {'high': '40780.87000000', 'low': '34850.00000000', 'timestamp': 1621468800}

        return new_markup


if __name__ == "__main__":
    db = Database()
    pairs = db.get_lines_by_chart_name_and_pair('BTCUSDT','BTCUSDT - LOCAL')
    print(pairs)
