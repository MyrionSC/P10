CREATE TYPE functionality.direction_map AS ENUM
    ('FORWARD', 'BACKWARD', 'BOTH');

CREATE TYPE functionality.direction_driving AS ENUM
    ('FORWARD', 'BACKWARD');

CREATE TYPE functionality.osm_categories AS ENUM
    ('ferry', 'motorway', 'motorway_link', 'trunk', 'trunk_link', 'primary', 'primary_link', 'secondary', 'secondary_link', 'tertiary', 'tertiary_link', 'unclassified', 'residential', 'living_street', 'service', 'road', 'track', 'unpaved', 'pedestrian', 'footway', 'cycleway', 'steps', 'path');
