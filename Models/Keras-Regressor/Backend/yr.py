import json
import db
import urllib.request
import urllib.parse
from xmltodict import parse as xmlParse
from Utils import url_ascii_encode

county_url_dict = {
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


def get_temperature(segment_id: int) -> int:
    """
    Get current yr temperature for segment

    :param segment_id:
    :return: (int) current temperature at segmentid
    """

    weather_data_dict, weather_station_county = _get_weather_data_dict(segment_id)

    # get the temperature now
    temperature = int(weather_data_dict['weatherdata']['forecast']['tabular']['time'][0]["temperature"]["@value"])

    print("Weatherstation for id " + str(segment_id) + " is " + weather_station_county + ". Temperature is " + str(
        temperature))

    return int(temperature)


def get_wind(segment_id: int) -> (float, float):
    """
    get current yr winddata at segment

    :param segment_id:
    :return: (float, float) return 2-tuple of floats where index 0 is winddirection in degrees and index 1 is windspeed in mps
    """

    weather_data_dict, weather_station_county = _get_weather_data_dict(segment_id)

    wind_direction_deg = float(weather_data_dict['weatherdata']['forecast']['tabular']['time'][0]['windDirection']['@deg'])
    wind_speed_mps = float(weather_data_dict['weatherdata']['forecast']['tabular']['time'][0]['windSpeed']['@mps'])

    return wind_direction_deg, wind_speed_mps


def _get_weather_data_dict(segment_id: int) -> (dict, str):
    # get county of segment_id
    weather_station_county = db.get_weather_station(segment_id)

    # retrieve data for county from yr
    url = county_url_dict[weather_station_county]
    return xmlParse(urllib.request.urlopen(url_ascii_encode(url)).read()), weather_station_county


def _get_coordinates_for_weatherstations():
    county_url_dict = json.loads(open("misc-data/TemperaturePlaceUrl.json").read())
    weatherstation_lat_long_dict = {}

    for key, value in dict.items(county_url_dict):
        print(key, value)
        result = urllib.request.urlopen(url_ascii_encode(value)).read()
        weather_data_dict = xmlParse(result)
        lat = weather_data_dict['weatherdata']['location']['location']['@latitude']
        long = weather_data_dict['weatherdata']['location']['location']['@longitude']
        weatherstation_lat_long_dict[key] = (lat, long)

    with open("misc-data/weatherstation-lat-long.txt", "w+") as file:  # creates / overwrites file
        for key, value in weatherstation_lat_long_dict.items():
            file.write(key + " " + value[0] + " " + value[1] + "\n")


def _parse_yr():
    place_url_dict = {}
    with open("misc-data/yr-denmark.txt", "r") as file:
        lines = file.readlines()

    for line in lines:
        linesplit = line.split("\t")
        county, url = linesplit[2], linesplit[len(linesplit) - 1].replace("forecast.xml", "forecast_hour_by_hour.xml")
        place_url_dict[county] = url.replace("\n", "")

    with open("misc-data/TemperaturePlaceUrl.json", "w+", encoding='utf8') as file:  # creates / overwrites file
        file.write(json.dumps(place_url_dict, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    print("temperature: " + str(get_temperature(1)))
    print("wind: " + str(get_wind(1)))
    # parseYr()
    # getCoordinates()
