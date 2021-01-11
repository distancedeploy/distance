from flask import Flask
from flask import request
import csv
import pandas as pd
from selenium import webdriver


# consts
NOT_VALID_STATUS = 400
BAD_CONNECTION_STATUS = 500
PORT_NUMBER = 8080
BASE_INDEX = 0
DB_NAME = 'distance.csv'
BAD_CONNECTION_MSG = "connection to DB is not OK"
distance_path = "https://www.distancefromto.net/"
driver = webdriver.Chrome()
app = Flask(__name__)
INVALID_INPUT_MSG = "invalid input"
MISSING_ARGUMENTS_MSG = "not enough argument were supplied"

# q1 - basic sol
@app.route('/hello')
def start():
    return ''


# q2
def get_answer_from_web(source, destination):
    """
    :param source: source city
    :param destination: destination city
    :return: distance between source and destination, given from the distance website
    """
    driver.get(distance_path)
    driver.find_element_by_id("distancefrom").send_keys(source)
    driver.find_element_by_id("distanceto").send_keys(destination)
    driver.find_element_by_id("hae").click()
    answer = driver.find_element_by_id("totaldistancekm").get_attribute("value")
    if answer: # if source and destination are valid cities
        answer = answer.split()
        return answer[BASE_INDEX]

    return ""


def modify_variables(theSource, theDestination):
    """
    :param theSource: source city
    :param theDestination: destination city
    :return: change to lower case, and switch so source will be smaller alphabetically
    """
    theSource, theDestination = theSource.lower(), theDestination.lower()
    if theSource > theDestination:
        theSource, theDestination = theDestination, theSource
    return theSource, theDestination


def find_distance_in_db(theSource, theDestination):
    df = pd.read_csv(DB_NAME)
    index = df[(df['Source'] == theSource) & (df['Destination'] == theDestination)].index.tolist()
    if index:
        return float(df[df['Source'] == theSource][df['Destination'] == theDestination]['Distance'])
    else:
        return -1


def update_csv(theSource, theDestination, distance):
    """
    :param theSource: source city
    :param theDestination: destination city
    :param distance: distance between cities
    :return: void, update the csvfile
    """
    row_to_append = [theSource, theDestination, str(distance)]
    with open(DB_NAME, 'a') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(row_to_append)
    csvfile.close()


# /distance?source=theSource&destination=theDestination
@app.route("/distance", methods=['GET'])
def find_distance():
    """
    :param theSource: source city
    :param theDestination: destination city
    :return: distance between source and destination
    """
    theSource, theDestination = request.args.get('source'), request.args.get('destination')

    if theSource is None or theDestination is None: # not enough arguments
        return MISSING_ARGUMENTS_MSG, NOT_VALID_STATUS

    else:
        theSource, theDestination = modify_variables(theSource, theDestination)
        distance = find_distance_in_db(theSource, theDestination)
        if distance >= 0: # found answer in DB - return it
            return "distance: " + str(distance)
        else:
            distance = get_answer_from_web(theSource, theDestination)
            if distance: # there is a valid answer - append it and return
                update_csv(theSource, theDestination, distance)
                return "distance: " + str(distance)
            else: # no valid answer - arguments were not valid cities
                return INVALID_INPUT_MSG, INVALID_INPUT_MSG

#q3
@app.route('/health')
def health():
    try:
        pd.read_csv(DB_NAME)
        return ""
    except:
        return BAD_CONNECTION_MSG, BAD_CONNECTION_STATUS

if __name__ == '__main__':
    app.run(port=PORT_NUMBER)
