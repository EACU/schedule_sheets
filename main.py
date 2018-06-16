import logging
import datetime
import pytz
import pygsheets
import sqlite3
from flask import Blueprint,render_template, abort
from jinja2 import TemplateNotFound
from flask_api import FlaskAPI
import json
from flask_cors import CORS

theme = Blueprint(
    'flask-api', __name__,
    url_prefix='/flask-api',
    template_folder='templates', static_folder='static'
)


app = FlaskAPI(__name__)
cors = CORS(app, resources={r"/getData/*": {"origins": "*"}})

app.config['DEFAULT_PARSERS'] = [
    'flask.ext.api.parsers.JSONParser',
    'flask.ext.api.parsers.URLEncodedParser',
    'flask.ext.api.parsers.MultiPartParser'
]
app.blueprints['flask-api'] = theme



@app.route('/')
def main():
 return render_template ('hello.html')

dayname = ['Понедельник','Вторник','Среда','Четверг','Пятница','Суббота','Воскресенье']

department = { 1:"D", 2:"E", 3:"F", 4:"G", 5:"H" }
timelessons = ["9:00 - 10:35", "10:45 - 12:20","14:45 - 16:20","16:30 - 18:05","18:15 - 19:50" ]
now = datetime.datetime.now()
nowWeek = datetime.datetime.today().isocalendar()[1]
evenOdd = ''
if (nowWeek % 2==0):
    evenOdd = "Чётная" 
else:
    evenOdd = "Нечётная"
gc = pygsheets.authorize(service_file='service_creds.json')
sh = gc.open('ScheduleInformatics')


@app.route('/getData/Info', methods=['GET'])
def info():
    """
    Информация о дне и неделе 
    """
    infoDay ={
        "parity" : evenOdd,
        "today" : dayname[datetime.datetime.today().weekday()],
        "weekdays" : dayname
        # "Визуальные коммуникации" : ["123", "223" , "323", "423"],
        # "Технологии управления в сфере культуры" : ["121", "221" , "321", "421"],
        # "Журналистика в области культуры" : ["122", "222" , "322", "422"],
        # "Танец и современная пластическая культура" : ["124", "224" , "324"],
        # "Прикладная информатика в социально-культурной сфере" : ["125", "225" , "325", "425"]
         }
    return infoDay



@app.route('/getData/<int:course>/<int:dept>', methods=['GET'])
def schedule(course,dept):
    table = f"{course}20({evenOdd})"
    f"""
    Расписание группы {table}
    """
    wks = sh.worksheet('title',table)
    start = f"{department[dept]}54"
    end = f"{department[dept]}4"
    week = wks.get_values(start, end, returnas='matrix', majdim='ROWS', value_render='UNFORMATTED_VALUE')
    jsonfile = { "group" : f"{course}2{dept}",
                 "parity" : evenOdd,
                 "today" : dayname[datetime.datetime.today().weekday()],
                 "week" : { 
                    dayname[0]: dict(zip(timelessons,week[0:6])),
                    dayname[1]: dict(zip(timelessons,week[9:15])),
                    dayname[2]: dict(zip(timelessons,week[18:24])),
                    dayname[3]: dict(zip(timelessons,week[27:33])),
                    dayname[4]: dict(zip(timelessons,week[36:42])),
                    dayname[5]: dict(zip(timelessons,week[45:51]))}
                }
    return jsonfile
            
@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8088, debug=True)

