import datetime

URL = 'https://motionera.stockholm/skridskoakning/'
DESTDIR_DEFAULT = 'dist/data/'

TIMEZONE = 'Europe/Stockholm'

# Constants declaration
ONE_DAY  = datetime.timedelta(days=1)
ONE_WEEK = datetime.timedelta(weeks=1)
DAYS   = ['Måndag', 'Tisdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lördag', 'Söndag']
MONTHS = ['januari', 'februari', 'mars', 'april', 'maj', 'juni', 'juli', 'augusti', 'september', 'oktober', 'november',  'december']

PLACES = [
    ('Farsta idrottsplats',          ['Ishallen']),
    ('Grimsta idrottsplats',         ['Ishallen']),
    ('Gubbängens idrottsplats',      ['Bandyhallen', 'Bandybana']),
    ('Husby ishall',                 None),
    ('Kärrtorps idrottsplats',       ['Ishallen']),
    ('Mälarhöjdens idrottsplats',    ['Ishallen']),
    ('Spånga idrottsplats',          ['Bandyplanen', 'Ishallen']),
    ('Stora Mossens idrottsplats',   ['A-hallen', 'B-hallen (HCL-hallen)']),
    ('Zinkensdamms idrottsplats',    ['Ishallen', 'Bandyplanen']),
    ('Östermalms idrottsplats',      ['Ishallen', 'Rundbana', 'Halvmåne, närmast Lidingövägen'])
]

# -- create structures for places identifiers --
def build_placenames():
    placenames = []
    offsets    = []
    s = 0

    for place, subplaces in PLACES:
        place = place.replace('idrottsplats', 'IP')

        if (subplaces is None) or len(subplaces) <= 1:
            placenames.append(place)
        else:
            placenames.extend(f'{place} ({subplace})' for subplace in subplaces)

        offsets.append(s)
        s += len(subplaces) if subplaces else 1

    return placenames, offsets

PLACENAMES, PLACES_OFFSETS = build_placenames()

