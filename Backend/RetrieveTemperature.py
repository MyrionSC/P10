import json
import db
import pprint
import urllib.request
from xmltodict import parse as xmlParse, unparse as xmlUnparse


def parseYr():
    placeUrlDict = {}
    with open("misc-data/yr-denmark.txt", "r") as file:
        lines = file.readlines()

    for line in lines:
        linesplit = line.split("\t")
        county, url = linesplit[2], linesplit[len(linesplit) - 1].replace("forecast.xml", "forecast_hour_by_hour.xml")
        placeUrlDict[county] = url.replace("\n", "")

    with open("misc-data/TemperaturePlaceUrl.json", "w+", encoding='utf8') as file:  # creates / overwrites file
        file.write(json.dumps(placeUrlDict, indent=4, ensure_ascii=False))



def RetrieveTemperature(segmentId: int):
    # get county of segmentId
    weatherStationCounty = db.getWeatherStation(segmentId)

    # retrieve data for county from yr
    countyUrlDict = json.loads(open("misc-data/TemperaturePlaceUrl.json").read())
    url = countyUrlDict[weatherStationCounty]
    weatherData = urllib.request.urlopen(url).read()
    # print(weatherData)

    print(json.dumps(xmlParse(weatherData), indent=4))






if __name__ == '__main__':
    # RetrieveTemperature("lksjdflkj")
    parseYr()


