import requests
import mysql.connector
from mysql.connector import Error
from datetime import datetime

def get_swell_data(latitude, longitude):
    url = f'https://barmmdrr.com/connect/gmarine_api?latitude={latitude}&longitude={longitude}&hourly=swell_wave_height,swell_wave_direction,swell_wave_period,swell_wave_peak_period'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print(f"[DEBUG] API Response Data: {data}")

        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='root_123',
                database='swa_db'
            )
            cursor = connection.cursor()

            # Insert location if not present
            insert_location_query = '''
            INSERT INTO locations (latitude, longitude) VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE location_id=LAST_INSERT_ID(location_id);
            '''
            cursor.execute(insert_location_query, (latitude, longitude))

            # Fetch the location_id
            cursor.execute('''SELECT location_id FROM locations WHERE latitude = %s AND longitude = %s''', (latitude, longitude))
            location_id = cursor.fetchone()
            if location_id:
                location_id = location_id[0]  # Extract the ID from the tuple
            else:
                print("[ERROR] Location ID retrieval failed after insertion.")
                return False

            # Store hourly swell data
            hourly_data = data.get('hourly', {})
            timestamps = hourly_data.get('time', [])
            swell_heights = hourly_data.get('swell_wave_height', [])
            swell_directions = hourly_data.get('swell_wave_direction', [])
            swell_periods = hourly_data.get('swell_wave_period', [])

            if not timestamps or not swell_heights or not swell_directions or not swell_periods:
                print("[ERROR] No hourly data found in the API response.")
                return False

            try:
                for i in range(len(timestamps)):
                    timestamp = datetime.strptime(timestamps[i], '%Y-%m-%dT%H:%M')
                    swell_height = swell_heights[i]
                    swell_direction = swell_directions[i]
                    swell_period = swell_periods[i]

                    insert_hourly_query = '''
                    INSERT INTO hourly_swell (location_id, time, swell_wave_height, swell_wave_direction, swell_wave_period)
                    VALUES (%s, %s, %s, %s, %s)
                    '''
                    cursor.execute(insert_hourly_query, (location_id, timestamp, swell_height, swell_direction, swell_period))

                print(f"[DEBUG] Successfully inserted hourly swell data for location ID {location_id}.")
            except Error as e:
                print(f"[ERROR] Error inserting hourly swell data: {e}")
                return False
            
            # Store current swell data
            current_height = swell_heights[0] if swell_heights else None
            current_direction = swell_directions[0] if swell_directions else None
            current_period = swell_periods[0] if swell_periods else None

            insert_current_query = '''
            INSERT INTO current_swell (location_id, time, swell_wave_height, swell_wave_direction, swell_wave_period)
            VALUES (%s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_current_query, (location_id, timestamps[0], current_height, current_direction, current_period))

            connection.commit()
            return True  # Indicate successful operation

        except Error as e:
            print(f"[ERROR] Database error: {e}")
            return False

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    else:
        print(f"[ERROR] API request failed with status: {response.status_code}")
        return False
