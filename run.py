from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import openpyxl
import time

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# mapping between card numbers and names. 
# follows the following structure:
# cardnumber: "name"
NAME_MAPPING = {
    260629: "Jonas Frankemölle"
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
        add_to_database(card_number)
        time.sleep(1)


def add_to_database(card_number):
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

    # write results to excel file
    today = datetime.now().strftime("%Y_%m_%d")
    result.to_excel("Kaffeeverbrauch_" + today + ".xlsx")
    # delete current db entries
    db.drop_all()
    return result # optional

if __name__=="__main__":
    # initialize database
    db.create_all()
    # call infinite loop
    get_user_input()