from flask import Flask, render_template, g, request
from datetime import datetime
from data.database import get_db

app = Flask(__name__)

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def pretty_date(date):
    dt = datetime.strptime(str(date), '%Y%m%d')
    return datetime.strftime(dt, '%B %d, %Y')


@app.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()

    if request.method == 'POST':
        # assuming the date is in YYYY/MM/DD format
        date = request.form['date']
        dt = datetime.strptime(date, '%Y-%m-%d')
        database_date = datetime.strftime(dt, '%Y%m%d')

        db.execute('INSERT INTO log_date (entry_date) values (?)',
                   [database_date])
        db.commit()

    cur = db.execute("""SELECT log_date.entry_date, sum(protein) as protein, sum(carbohydrates) as carbohydrates, sum(fat) as fat, sum(calories) as calories
                        FROM log_date
                        JOIN food_dates ON food_dates.log_date_id = log_date.id
                        JOIN food ON food.id = food_dates.food_id
                        GROUP BY log_date.id ORDER BY entry_date DESC""")
    results = cur.fetchall()

    date_results = []

    for i in results:
        single_date = {}
        single_date['entry_date'] = i['entry_date']
        single_date['protein'] = i['protein']
        single_date['carbohydrates'] = i['carbohydrates']
        single_date['fat'] = i['fat']
        single_date['calories'] = i['calories']

        single_date['pretty_date'] = pretty_date(i['entry_date'])

        date_results.append(single_date)

    return render_template('home.html', results=date_results)


# date is going to be 20170214
@app.route('/view/<date>', methods=['GET', 'POST'])
def view(date):
    db = get_db()

    cur = db.execute(
        'SELECT id, entry_date FROM log_date WHERE entry_date = ?', [date])
    date_result = cur.fetchone()

    if request.method == 'POST':
        db.execute('INSERT INTO food_dates values (?,?)', [
                   request.form['food-select'], date_result['id']])
        db.commit()

    cur = db.execute('SELECT id, name FROM food')
    food_results = cur.fetchall()

    cur = db.execute("""SELECT name, protein, carbohydrates, fat, calories, entry_date
                        FROM log_date
                        JOIN food_dates ON food_dates.log_date_id = log_date.id
                        JOIN food ON food.id = food_dates.food_id
                        WHERE entry_date = ?""", [date])
    food_dates_results = cur.fetchall()

    totals = {'protein' : 0, 'carbohydrates' : 0, 'fat' : 0, 'calories' : 0}

    for food in food_dates_results:
        totals['protein'] += food['protein']
        totals['carbohydrates'] += food['carbohydrates']
        totals['fat'] += food['fat']
        totals['calories'] += food['calories']

    return render_template('day.html',
                           date={'pretty':pretty_date(date_result['entry_date']),'entry':date},
                           food_results=food_results,
                           food_dates_results=food_dates_results,
                           totals=totals)


@app.route('/food', methods=['GET', 'POST'])
def food():
    db = get_db()

    if request.method == 'POST':
        name = request.form["name"]
        protein = int(request.form["protein"])
        carbohydrates = int(request.form["carbohydrates"])
        fat = int(request.form["fat"])

        calories = protein * 4 + carbohydrates * 4 + fat * 9

        db.execute('insert into food (name, protein, carbohydrates, fat, calories) values (?,?,?,?,?)',
                   [name, protein, carbohydrates, fat, calories])

        db.commit()

    cur = db.execute(
        'SELECT name, protein, carbohydrates, fat, calories FROM food')
    results = cur.fetchall()

    return render_template('add_food.html', results=results)


if __name__ == '__main__':
    app.run(debug=True)
