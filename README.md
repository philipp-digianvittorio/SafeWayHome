# SafeWayHome
## Scope of the project
- scrape incidents from presseportal.de, categorize incidents (train on one city, demonstrate for another one)
- map incidents on open street view map
- scrape street view images from google maps, set up survey to determine safety perception
- (include parks/underpasses/industrial areas) on district area
- calculate "creepiness-score" for different streets/areas
- set up map with green/yellow/red areas according to score (Choropleth)
- (extension: reporting feature "I felt unsafe here")

## Next steps/Tasks (due 25.01.23)
Done:
- Maren/Stella: set up and run survey -> DONE
- write function which finds safest route -> theoretisch ja

Almost done:
- add plotly map into app -> fast DONE (drop duplicate plot on second page)
- Philipp: try out new deep learning tools
- use start and destination from input boxes to compute route (to do for plotly map)
- manipulate OSM data (weight distance with Creepinessscore) -> Computation for all edges in FFM takes very long (48h) -> parallelize? Cluster?

Not yet done:
- decide how to compute Creepinessscore
- finally classify articles
- maybe make choropleth map with coloured districts? 
- deploy app in bwCloud (potentailly problematic, help needed) 
- Video drehen... O_o (potentailly embarrasing)

## Open Questions/Issues
- classification: 
  - incidents that fall into more than one category
  - no street name/only street number
  - "Vortäuschen einer Straftat" -> filter out before extracting street name
- interface:
  - pins with incidents: over Street names or coordinates?
  - dropdown with 2 cities (coordinates would be fixed) -> Nope
- webscraping -> DONE

## Useful Links
### Interface
- http://bl.ocks.org/williaster/95584ebda56f5345b709
- https://mateuszwiza.medium.com/plotting-api-results-on-a-map-using-flask-and-leafletjs-2cf2d3cc660b
- https://sbhadra019.medium.com/interactive-webmap-using-python-8b11ba2f5f0f
- https://wiki.openstreetmap.org/wiki/Tag:leisure%3Dpark
