import json
import db
import urllib.request
import urllib.parse
from xmltodict import parse as xmlParse
from Utils import urlAsciiEncode

countyUrlDict = {
    "Taastrup": "http://www.yr.no/place/Denmark/Capital/Taastrup/forecast_hour_by_hour.xml",
    "Næstved": "http://www.yr.no/place/Denmark/Zealand/Næstved/forecast_hour_by_hour.xml",
    "Sorø": "http://www.yr.no/place/Denmark/Zealand/Sorø/forecast_hour_by_hour.xml",
    "Holstebro": "http://www.yr.no/place/Denmark/Central_Jutland/Holstebro/forecast_hour_by_hour.xml",
    "Silkeborg": "http://www.yr.no/place/Denmark/Central_Jutland/Silkeborg/forecast_hour_by_hour.xml",
    "Vejle": "http://www.yr.no/place/Denmark/South_Denmark/Vejle/forecast_hour_by_hour.xml",
    "Rønne": "http://www.yr.no/place/Denmark/Capital/Rønne/forecast_hour_by_hour.xml",
    "Århus": "http://www.yr.no/place/Denmark/Central_Jutland/Aarhus/forecast_hour_by_hour.xml",
    "Frederikshavn": "http://www.yr.no/place/Denmark/North_Jutland/Frederikshavn/forecast_hour_by_hour.xml",
    "Brønderslev": "http://www.yr.no/place/Denmark/North_Jutland/Brønderslev/forecast_hour_by_hour.xml",
    "Slagelse": "http://www.yr.no/place/Denmark/Zealand/Slagelse/forecast_hour_by_hour.xml",
    "Helsingør": "http://www.yr.no/place/Denmark/Capital/Elsinore/forecast_hour_by_hour.xml",
    "Hillerød": "http://www.yr.no/place/Denmark/Capital/Hillerød/forecast_hour_by_hour.xml",
    "Sønderborg": "http://www.yr.no/place/Denmark/South_Denmark/Sønderborg/forecast_hour_by_hour.xml",
    "Svendborg": "http://www.yr.no/place/Denmark/South_Denmark/Svendborg/forecast_hour_by_hour.xml",
    "Esbjerg": "http://www.yr.no/place/Denmark/South_Denmark/Esbjerg/forecast_hour_by_hour.xml",
    "Randers": "http://www.yr.no/place/Denmark/Central_Jutland/Randers/forecast_hour_by_hour.xml",
    "Roskilde": "http://www.yr.no/place/Denmark/Zealand/Roskilde/forecast_hour_by_hour.xml",
    "Hobro": "http://www.yr.no/place/Denmark/North_Jutland/Hobro/forecast_hour_by_hour.xml",
    "Odense": "http://www.yr.no/place/Denmark/South_Denmark/Odense/forecast_hour_by_hour.xml",
    "Smidstrup": "http://www.yr.no/place/Denmark/Capital/Smidstrup~2613357/forecast_hour_by_hour.xml",
    "Hørsholm": "http://www.yr.no/place/Denmark/Capital/Hørsholm/forecast_hour_by_hour.xml",
    "Køge": "http://www.yr.no/place/Denmark/Zealand/Køge/forecast_hour_by_hour.xml",
    "Hjørring": "http://www.yr.no/place/Denmark/North_Jutland/Hjørring/forecast_hour_by_hour.xml",
    "Viborg": "http://www.yr.no/place/Denmark/Central_Jutland/Viborg/forecast_hour_by_hour.xml",
    "Greve": "http://www.yr.no/place/Denmark/Zealand/Greve/forecast_hour_by_hour.xml",
    "Ålborg": "http://www.yr.no/place/Denmark/North_Jutland/Aalborg/forecast_hour_by_hour.xml",
    "Herning": "http://www.yr.no/place/Denmark/Central_Jutland/Herning/forecast_hour_by_hour.xml",
    "København": "http://www.yr.no/place/Denmark/Capital/Copenhagen/forecast_hour_by_hour.xml"
}

def getTemperature(segmentId: int) -> int:
    """
    Get current yr temperature for segment

    :param segmentId:
    :return: (int) current temperature at segmentid
    """

    weatherDataDict, weatherStationCounty = _getWeatherDataDict(segmentId)

    # get the temperature now
    temperature = int(weatherDataDict['weatherdata']['forecast']['tabular']['time'][0]["temperature"]["@value"])

    print("Weatherstation for id " + str(segmentId) + " is " + weatherStationCounty + ". Temperature is " + str(temperature))

    return int(temperature)

def getWind(segmentId: int) -> (float, float):
    """
    get current yr winddata at segment

    :param segmentId:
    :return: (float, float) return 2-tuple of floats where index 0 is winddirection in degrees and index 1 is windspeed in mps
    """

    weatherDataDict, weatherStationCounty = _getWeatherDataDict(segmentId)

    windDirectionDeg = float(weatherDataDict['weatherdata']['forecast']['tabular']['time'][0]['windDirection']['@deg'])
    windSpeedMps = float(weatherDataDict['weatherdata']['forecast']['tabular']['time'][0]['windSpeed']['@mps'])

    return windDirectionDeg, windSpeedMps


def _getWeatherDataDict(segmentId: int) -> (dict, str):
    # get county of segmentId
    weatherStationCounty = db.getWeatherStation(segmentId)

    # retrieve data for county from yr
    url = countyUrlDict[weatherStationCounty]
    return xmlParse(urllib.request.urlopen(urlAsciiEncode(url)).read()), weatherStationCounty

def _getCoordinatesForWeatherstations():
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

def _parseYr():
    placeUrlDict = {}
    with open("misc-data/yr-denmark.txt", "r") as file:
        lines = file.readlines()

    for line in lines:
        linesplit = line.split("\t")
        county, url = linesplit[2], linesplit[len(linesplit) - 1].replace("forecast.xml", "forecast_hour_by_hour.xml")
        placeUrlDict[county] = url.replace("\n", "")

    with open("misc-data/TemperaturePlaceUrl.json", "w+", encoding='utf8') as file:  # creates / overwrites file
        file.write(json.dumps(placeUrlDict, indent=4, ensure_ascii=False))




if __name__ == '__main__':
    print("temperature: " + str(getTemperature(1)))
    print("wind: " + str(getWind(1)))
    # parseYr()
    # getCoordinates()


