# Data quality report

Source: seeded synthetic generator

Input rows: 6410

Clean rows: 6410

Exact duplicate rows removed: 0

Required schema columns: airline, arrival_time, class, days_left, departure_time, destination_city, duration, flight, price, source_city, stops

Days left range: 1–60

Duration range (hours): 1.02–7.99

Fare range (INR): 1746.68–91278.74

Class counts: {'Economy': 5118, 'Business': 1292}

Stops counts: {'zero': 3364, 'one': 2771, 'two_or_more': 275}

Flagged price outliers (retained): 3

Distinct horizons per flight-route-class panel: min 10, median 13, max 14

Rows at different horizons may represent different physical departures. Synthetic values are illustrative, not observed market data.

## City directory

The route form includes a static directory of Indian airport cities maintained in `configs/cities.yaml`, compiled from Airports Authority of India airport and aerodrome lists ([operational airport FAQ](https://www.aai.aero/en/faqs), [licensed aerodromes](https://www.aai.aero/en/content/aerodrome-licensing)). The directory is a destination picker, not a guarantee of scheduled service or route-level fare history. The current synthetic sample still contains fares for only six cities; unsupported routes are clearly reported or use a labeled class-wide estimate fallback.
