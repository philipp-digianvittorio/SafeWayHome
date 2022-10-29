# SafeWayHome
## Outline
- scrape incidents from presseportal.de, categorize incidents (train on one city, demonstrate for another one)
- map incidents on open street view map
- set up map with green/yellow/red areas according to safety issues
- include parks/underpasses/industrial areas
- (extension: reporting feature "I felt unsafe here")

## Open Questions/Issues
- classification: 
  - incidents that fall into more than one category
  - no street name/only street number
  - "Vortäuschen einer Straftat" - extra category or dismiss?
- interface:
  - pins with incidents: over Street names or coordinates?
  - dropdown with 2 cities (coordinates would be fixed)

## Useful Links
### Interface
- http://bl.ocks.org/williaster/95584ebda56f5345b709
- https://mateuszwiza.medium.com/plotting-api-results-on-a-map-using-flask-and-leafletjs-2cf2d3cc660b
- https://sbhadra019.medium.com/interactive-webmap-using-python-8b11ba2f5f0f
- https://wiki.openstreetmap.org/wiki/Tag:leisure%3Dpark
