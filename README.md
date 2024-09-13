
# GeoLite2 City IP Lookup Service

This project is a Flask-based service that queries a PostgreSQL database to retrieve location data associated with IP address ranges using the GeoLite2 dataset.

## Features

- Query IP addresses to get location information including country, city, state, coordinates, and timezone.

## Prerequisites

Download the most up to date GeoLite2 dataset.
```
wget -qO-  https://cdn.jsdelivr.net/npm/@ip-location-db/geolite2-city/geolite2-city-ipv4.csv.gz  | gunzip > app/city_data.csv
```

## Quick Start

```bash
git clone https://github.com/yourusername/geolite2-ip-lookup.git
cd geolite2-ip-lookup
docker-compose up --build
```

Access http://localhost:9000/ip_to_loc/1.0.64.0 to test.



