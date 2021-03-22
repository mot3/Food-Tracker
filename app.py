from flask import Flask, render_template, g, Request  
import sqlite3

from flask.globals import request

app = Flask(__name__)

def connect_db():
    sql = sqlite3.connect('./data/food_log.db')
    sql.row_factory = sqlite3.Row
    return sql

def get_db():
    if not hasattr(g, 'sqlite3_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'): 
        g.sqlite_db.close()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/view')
def view():
    return render_template('day.html')

@app.route('/food', methods=['GET','POST'])
def food():
    if request.method == 'POST':
        return f'<h1>Name: {request.form["name"]}, Protein: {request.form["protein"]}, Carbohydrates: {request.form["carbohydrates"]}, Fat: {request.form["fat"]}</h1>' 
    return render_template('add_food.html')

if __name__ == '__main__':
    app.run(debug=True)