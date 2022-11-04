# SafeWayHome
## Scope of the project
- scrape incidents from presseportal.de, categorize incidents (train on one city, demonstrate for another one)
- map incidents on open street view map
- scrape street view images from google maps, set up survey to determine safety perception
- include parks/underpasses/industrial areas
- calculate "creepiness-score" for different streets/areas
- set up map with green/yellow/red areas according to score
- (extension: reporting feature "I felt unsafe here")

## Next steps/Tasks (due 18.11.22)
- Maren/Stella: set up and run survey
- Philipp: try out new deep learning tools

## Open Questions/Issues
- classification: 
  - incidents that fall into more than one category
  - no street name/only street number
  - "Vortäuschen einer Straftat" -> filter out before extracting street name
- interface:
  - pins with incidents: over Street names or coordinates?
  - dropdown with 2 cities (coordinates would be fixed)
- webscraping:
  - filter dienststellen by police department or not 
  - format of column article should only contain text
  - how to get last page?

## Useful Links
### Interface
- http://bl.ocks.org/williaster/95584ebda56f5345b709
- https://mateuszwiza.medium.com/plotting-api-results-on-a-map-using-flask-and-leafletjs-2cf2d3cc660b
- https://sbhadra019.medium.com/interactive-webmap-using-python-8b11ba2f5f0f
- https://wiki.openstreetmap.org/wiki/Tag:leisure%3Dpark
