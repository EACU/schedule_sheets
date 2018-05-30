import logging
import datetime
import pygsheets
from flask import Blueprint,render_template, abort
from jinja2 import TemplateNotFound
from flask_api import FlaskAPI

theme = Blueprint(
    'flask-api', __name__,
    url_prefix='/flask-api',
    template_folder='templates', static_folder='static'
)

app = FlaskAPI(__name__)
app.blueprints['flask-api'] = theme
dayname    = ['Понедельник','Вторник','Cреда','Четверг','Пятница','Cуббота']
nowWeek = datetime.datetime.today().isocalendar()[1]
evenOdd = ''
if (nowWeek % 2==0):
    evenOdd = "Чётная" 
else:
    evenOdd = "Нечетная"


@app.route('/')
def main():
 return render_template ('hello.html')


@app.route('/Info', methods=['GET'])
def info():
    """
    Информация о дне и неделе 
    """
    infoDay ={
        "Четность" : evenOdd,
        "Cегодня" : dayname[datetime.datetime.today().weekday()] }
    return infoDay



@app.route('/getData/<course>/<int:group>', methods=['GET'])
def schedule(course,group):
    f"""
    Расписание на неделю 
    """

    department = { 1:4, 2:5, 3:6, 4:7, 5:8 }
    gc = pygsheets.authorize(service_file='service_creds.json')
    sh = gc.open('ScheduleInformatics')
    table = f"{course}20({evenOdd})"
    wks = sh.worksheet('title',table)
    def courses(courses):
        # Один поток заполняет шесть дней
        week = {}
        daylesson  = { 4:9, 13:18, 22:27, 31:36, 40:45, 49:54 }
        day = 0
        for key in daylesson.keys():
            lessons = wks.get_values(start=(key,courses), end=(daylesson[key],courses), returnas='matrix')
            week[dayname[day]] = lessons
            day = day+1
        return week
    

    return  courses(department[group])

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8088, debug=True)

