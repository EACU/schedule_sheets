import logging
import datetime
import pygsheets
import sqlite3
from flask import Blueprint,render_template, abort
from jinja2 import TemplateNotFound
from flask_api import FlaskAPI
import json
theme = Blueprint(
    'flask-api', __name__,
    url_prefix='/flask-api',
    template_folder='templates', static_folder='static'
)

app = FlaskAPI(__name__)
app.blueprints['flask-api'] = theme



@app.route('/')
def main():
 return render_template ('hello.html')

dayname    = ['Понедельник','Вторник','Cреда','Четверг','Пятница','Cуббота']
department = { 1:"D", 2:"E", 3:"F", 4:"G", 5:"H" }
nowWeek = datetime.datetime.today().isocalendar()[1]
evenOdd = ''
if (nowWeek % 2==0):
    evenOdd = "Чётная" 
else:
    evenOdd = "Нечётная"
gc = pygsheets.authorize(service_file='service_creds.json')
sh = gc.open('ScheduleInformatics')


@app.route('/Info', methods=['GET'])
def info():
    """
    Информация о дне и неделе 
    """
    infoDay ={
        "Четность" : evenOdd,
        "Cегодня" : dayname[datetime.datetime.today().weekday()] }
    return infoDay



@app.route('/getData/<int:course>/<int:dept>', methods=['GET'])
def schedule(course,dept):
    table = f"{course}20({evenOdd})"
    wks = sh.worksheet('title',table)
    start = f"{department[dept]}54"
    end = f"{department[dept]}4"
    week = wks.get_values(start, end, returnas='matrix', majdim='ROWS', value_render='FORMATTED_VALUE')
    return {"Неделя сейчас" :evenOdd,
            "Cегодня" : dayname[datetime.datetime.today().weekday()],
            dayname[0]: week[0:6],
            dayname[1]: week[9:15],
            dayname[2]: week[18:24],
            dayname[3]: week[27:33],
            dayname[4]: week[36:42],
            dayname[5]: week[45:51],}

conn = sqlite3.connect('Schedule.sqlite')
cursor = conn.cursor()


conn.close()


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8088,debug=True)

