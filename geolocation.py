from flask import Flask
import csv
import pandas as pd
from selenium import webdriver

distance_path = "https://www.distancefromto.net/"
driver = webdriver.Chrome()
app = Flask(__name__)

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
        return answer[0]

    return ""

@app.route("/distance/source=<theSource>/destination=<theDestination>")
def find_distance(theSource, theDestination):
    """
    :param theSource: source city
    :param theDestination: destination city
    :return: distance between source and destination
    """
    theSource, theDestination = theSource.lower(), theDestination.lower()
    df = pd.read_csv('distance.csv')
    #  take source as the smaller alphabetic
    if theSource > theDestination:
        theSource, theDestination = theDestination, theSource

    # check if the distance between theSource and theDestination is in the DB
    index = df[(df['Source'] == theSource) & (df['Destination'] == theDestination)].index.tolist()
    if index:
        return "distance: " + str(float(df[df['Source'] == theSource][df['Destination'] == theDestination]['Distance']))

    # didnt find - so check web
    else:
        numberOfkMs = get_answer_from_web(theSource, theDestination)
        if numberOfkMs: # there is a valid answer - append it and return
            # add it to csv
            row_to_append = [theSource, theDestination, str(numberOfkMs)]
            with open('distance.csv', 'a') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(row_to_append)
            # return result
            return "distance: " + str(numberOfkMs)
        else:
            return "input not valid"


@app.route('/health')
def health():
    try:
        pd.read_csv('distance.csv')
        return ""
    except:
        return "connection to DB is not OK"

if __name__ == '__main__':
    app.run(port=8080)
