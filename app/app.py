import csv
import json
import os

from flask import Flask
import psycopg

app = Flask(__name__)

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 6600))
DB_NAME = os.getenv('DB_NAME', 'postgres')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')


def create_connection():
    return psycopg.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )


def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS public.geolite2_city_ipv4 (
        ip_range_start INET NOT NULL,
        ip_range_end INET NOT NULL,
        country_code VARCHAR(2) NOT NULL,
        city VARCHAR(255),
        state1 VARCHAR(255),
        state2 VARCHAR(255),
        latitude NUMERIC(9,6),
        longitude NUMERIC(9,6),
        postcode VARCHAR(20),
        timezone VARCHAR(255) NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_ip_range_start ON geolite2_city_ipv4 (ip_range_start);
    CREATE INDEX IF NOT EXISTS idx_ip_range_end ON geolite2_city_ipv4 (ip_range_end);
    '''
    cursor.execute(create_table_query)
    conn.commit()

    query = '''
        INSERT INTO geolite2_city_ipv4 (
            ip_range_start, ip_range_end, country_code, city, state1, state2, latitude, longitude, postcode, timezone
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        '''

    conn.autocommit = True
    with open('city_data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)

        with conn.pipeline():
            for row in reader:
                cursor.execute(query, [None if value == '' else value for value in row])

    conn.commit()
    conn.close()


@app.route('/ip_to_loc/<path:ip>')
def search(ip):
    query = '''
        SELECT ip_range_start, ip_range_end, country_code, city, state1, state2, latitude, longitude, postcode, timezone
        FROM geolite2_city_ipv4
        WHERE ip_range_start <= %s::inet AND ip_range_end >= %s::inet
        LIMIT 1;
    '''

    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(query, (ip, ip))
        result = cursor.fetchone()

        if result:
            location_data = {
                "ip_range_start": str(result[0]),
                "ip_range_end": str(result[1]),
                "country_code": result[2],
                "city": result[3],
                "state1": result[4],
                "state2": result[5],
                "latitude": float(result[6]) if result[6] is not None else None,
                "longitude": float(result[7]) if result[7] is not None else None,
                "postcode": result[8],
                "timezone": result[9]
            }
            return json.dumps(location_data)
        else:
            return json.dumps({"error": "IP not found"}), 404
    finally:
        conn.close()


if __name__ == '__main__':
    create_table()
    app.run(host="0.0.0.0", port=9000, debug=False)

