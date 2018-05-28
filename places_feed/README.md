# Places Feed Generator

Takes a database with the `osm_polygon` table and prepares three lists:
of countries, regions and places, complete with hierarchy. These files
are enriched with translations taken from Wikidata, and tested against
a big list of cities and capitals.

Just run `places_feed.sh`. Alternatively, you can use separate scripts:

* `places_feed.py`: prepares json files from the `osm_polygon` table.
* `translate_places.py`: queries Wikidata and adds more translations to json files.
* `validate_cities.py`: tests the completeness of the feeds.
* `flat_json_to_csv.py`: converts json to csv.

If you just need the files, you can take [some of ours](http://seofeed.maps.me/website/places/).
