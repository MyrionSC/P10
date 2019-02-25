import json
import db
import urllib.request
import urllib.parse
from xmltodict import parse as xmlParse
from Utils import urlAsciiEncode


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
    weatherDataDict = xmlParse(urllib.request.urlopen(urlAsciiEncode(url)).read())

    # get the temperature now
    temperature = int(weatherDataDict['weatherdata']['forecast']['tabular']['time'][0]["temperature"]["@value"])

    print("Weatherstation for id " + str(segmentId) + " is " + weatherStationCounty + ". Temperature is " + str(temperature))

    return int(temperature)


def getCoordinates():
    countyUrlDict = json.loads(open("misc-data/TemperaturePlaceUrl.json").read())
    weatherstationLatLongDict = {}

    for key, value in dict.items(countyUrlDict):
        print(key, value)
        result = urllib.request.urlopen(urlAsciiEncode(value)).read()
        weatherDataDict = xmlParse(result)
        lat = weatherDataDict['weatherdata']['location']['location']['@latitude']
        long = weatherDataDict['weatherdata']['location']['location']['@longitude']
        weatherstationLatLongDict[key] = (lat, long)

    with open("misc-data/weatherstation-lat-long.txt", "w+") as file:  # creates / overwrites file
        for key, value in weatherstationLatLongDict.items():
            file.write(key + " " + value[0] + " " + value[1] + "\n")



if __name__ == '__main__':
    pass
    # print("temperature: " + str(RetrieveTemperature(1)))
    # parseYr()
    # getCoordinates()


