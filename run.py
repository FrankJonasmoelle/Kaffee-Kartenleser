from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
import matplotlib.pyplot as plt
import openpyxl
import time

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# set price for one cup of coffee (€)
COFFEE_PRICE = 0.7

# mapping between card numbers and names. 
# follows the following structure:
# cardnumber: "name"
NAME_MAPPING = {
    260629: "Jonas Frankemölle",
    244684: "Thomas Wiedemann",
    260647: "Sooyeon Cho", 
    260009: "Borja Sanchez",
    248061: "Constantin Radzio",
    260762: "Julius Erdmann",
    505823: "Julia Neubert",
    239024: "Sabrina Mothes",
    246025: "Marc-David Jung",
    247394: "Marius Mutter"
}

# Database Model
class CoffeeModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cardnumber = db.Column(db.Integer)
    date = db.Column(db.DateTime)

    def __init__(self, cardnumber, date):
        self.cardnumber = cardnumber
        self.date = date


# Basic Python functions

def get_user_input():
    while True:
        print('waiting for input')
        card_number = input()
        print('new card number: ', card_number)
        # add card number to database
        add_entry_to_db(card_number)
        time.sleep(1)


def add_entry_to_db(card_number):
    new_entry = CoffeeModel(cardnumber=card_number, date=datetime.utcnow())
    db.session.add(new_entry)
    db.session.commit()

def get_coffee_consumption():
    # get data
    data = CoffeeModel.query.all()
    # store cardnumbers in dict
    card_nums = {dat.id: dat.cardnumber for dat in data}
    # create dataframe
    df = pd.DataFrame(card_nums.items(), columns=['Anzahl', 'Kartennummer'])
    # rename Kartennummer with real names from 'NAME_MAPPING' dict
    df['Kartennummer'] = df.Kartennummer.replace(NAME_MAPPING)
    # for each card number: count occurances
    result = df.groupby('Kartennummer').count()
    # add column with total cost for coffees
    result['Betrag [€]'] = result['Anzahl'] * COFFEE_PRICE

    # write results to excel file
    today = datetime.now().strftime("%Y_%m_%d")
    result.to_excel("Kaffeeverbrauch_" + today + ".xlsx")

    # delete current db entries
    db.drop_all()
    return result # optional

def print_coffee_consumption():
    # get data
    data = CoffeeModel.query.all()
    # store cardnumbers in dict
    card_nums = {dat.id: dat.cardnumber for dat in data}
    # create dataframe
    df = pd.DataFrame(card_nums.items(), columns=['Anzahl', 'Kartennummer'])
    # rename Kartennummer with real names from 'NAME_MAPPING' dict
    df['Kartennummer'] = df.Kartennummer.replace(NAME_MAPPING)
    # for each card number: count occurances
    result = df.groupby('Kartennummer').count()
    # add column with total cost for coffees
    result['Betrag [€]'] = result['Anzahl'] * COFFEE_PRICE
    return result 


def evaluate_coffee_consumption():
    data = CoffeeModel.query.all()
    # store cardnumbers and time in dict
    nums = [dat.cardnumber for dat in data]
    timestmps = [dat.date for dat in data]
    data = {'cardnumber': nums, 'Timestamp': timestmps}
    # create dataframe
    df = pd.DataFrame(data)
    return df


if __name__=="__main__":
    # initialize database
    db.create_all()
    
    # instantiate scheduler to execute 'get_coffee_consumption' at the end of each month
    sched = BackgroundScheduler(deamon=True)
    sched.add_job(get_coffee_consumption, 'cron', day='last')
    sched.start()
    
    # call infinite loop
    get_user_input()