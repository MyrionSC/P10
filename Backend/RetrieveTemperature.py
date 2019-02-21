import json
import db
import pprint
import urllib.request
import datetime
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



def RetrieveTemperature(segmentId: int) -> int:
    # get county of segmentId
    weatherStationCounty = db.getWeatherStation(segmentId)

    # retrieve data for county from yr
    countyUrlDict = json.loads(open("misc-data/TemperaturePlaceUrl.json").read())
    url = countyUrlDict[weatherStationCounty]
    weatherDataDict = xmlParse(urllib.request.urlopen(url).read())

    # with open("weatherdump.json", "w+") as file:  # creates / overwrites file
    #     file.write(json.dumps(weatherDataDict, indent=4))
    # with open("weatherdump.json", "r") as file:
    #     weatherDataDict = json.loads(file.read())

    # get the temperature now
    return int(weatherDataDict['weatherdata']['forecast']['tabular']['time'][0]["temperature"]["@value"])




if __name__ == '__main__':
    print("temperature: " + str(RetrieveTemperature(2)))
    # parseYr()


