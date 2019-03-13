import json

import Utils.SQL as db
import Utils.LocalSettings as settings
from pprint import pprint
import pandas as pd

known_energy_trips = [116699, 91881, 4537, 76966, 52557, 175355, 103715]

data = {
    'known_energy_route_data': [],
    'unknown_energy_route_data': []
}

# grab information for known energy trips
for trip_id in known_energy_trips:
    trip_segs, meta = db.get_trip_info(trip_id, settings.main_db)
    trip_segs_df = pd.DataFrame(trip_segs)

    trip_data = {
        'trip_id': trip_id,
        'ev_kwh_trip': trip_segs_df['ev_kwh_trip'].values[-1],
        'seconds_trip': trip_segs_df['seconds_trip'].values[-1],
        'segments': [
            {
                'segmentkey': int(trip_segs_df['segmentkey'][i]),
                'direction': trip_segs_df['direction'][i]
            }
            for i in range(len(trip_segs_df['segmentkey']))]
    }
    data['known_energy_route_data'].append(trip_data)



# compile data for unknown energy trips




# save to file
filepath = "../downloads/candidate-routes.json"
with open(filepath, "w+") as file:  # creates / overwrites file
    file.write(json.dumps(data, indent=4))
    print("file saved to " + filepath)



