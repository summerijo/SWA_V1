from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, get_flashed_messages
import mysql.connector
from mysql.connector import Error
from api_routes import api
from fetch_data import get_swell_data

app = Flask(__name__)
app.secret_key = 'dev' 

# Register the Blueprint for API routes
app.register_blueprint(api)

# MySQL configuration
db_config = {
    'host': 'localhost',
    'user': 'root',      
    'password': '12345678',
    'database': 'swa_v1'
}

# Helper function to connect to the database
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn
@app.route('/home')
def home():
    return render_template('home.html')
# CREATE Operation (Register a new user)
@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        fname = request.form['firstName']
        lname = request.form['lastName']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        contact = request.form['contact']
        

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            query = "INSERT INTO users (f_name, l_name, email, username, password, contact_number) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (fname, lname, email, username, password, contact))
            conn.commit()

            # Flash a success message and render the same page
            flash('You have successfully registered. Please log in.', 'success')
            return render_template('register.html')
        
        except mysql.connector.Error as err:
            return jsonify({'error': str(err)})
        
        finally:
            cursor.close()
            conn.close()
    return render_template('register.html')

# READ Operation (List all users)
@app.route('/users')
def list_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('users.html', users=users)

# UPDATE Operation (Edit a user's information)
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        fname = request.form['firstName']
        lname = request.form['lastName']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        contact = request.form['contact']

        query = "UPDATE users SET f_name = %s, l_name = %s, email = %s, username = %s, password = %s, contact_number = %s WHERE user_id = %s"
        cursor.execute(query, (fname, lname, email, username, password, contact, id))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('list_users'))

    else:
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('edit_user.html', user=user)

# DELETE Operation (Delete a user)
@app.route('/delete/<int:id>')
def delete_user(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('list_users'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None  # Initialize an error message variable
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Query to find the user by email
            query = "SELECT * FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()

            # If user exists and the password matches
            if user and user['password'] == password:
                session['email'] = email 
                return redirect(url_for('maps'))
            else:
                error = 'Invalid credentials, please try again.'
                
        except mysql.connector.Error as err:
            error = f"Database error: {err}"

        finally:
            # Ensure any unread results are handled before closing
            cursor.fetchall()  # Clear any potential remaining results
            cursor.close()
            conn.close()

    return render_template('login.html', error=error)


# Logout Route
@app.route('/logout')
def logout():
    session.pop('email', None)  # Remove the user from session
    return redirect(url_for('login'))

# Protected Route (Maps Page)
@app.route('/maps')
def maps():
    if 'email' in session:  # Check if user is logged in
        return render_template('maps.html', email=session['email'])
    else:
        return redirect(url_for('login'))
    
@app.route('/animation')
def animation():
    return render_template('animation.html')

@app.route('/get-stored-data', methods=['POST'])
def get_stored_data():
    data = request.get_json()
    latitude = float(data['latitude'])
    longitude = float(data['longitude'])

    print(f"[DEBUG] Received Latitude: {latitude}, Longitude: {longitude}")

    try:
        # Establish connection to the database
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Attempt to find the location ID based on latitude and longitude
        cursor.execute('''SELECT location_id FROM locations
                          WHERE latitude = CAST(%s AS DECIMAL(10, 7))
                          AND longitude = CAST(%s AS DECIMAL(10, 7))''',
                       (latitude, longitude))
        location = cursor.fetchone()  # Fetch the first result

    
        # If location is not found, fetch data from the API
        if not location:
            print("[DEBUG] Location not found. Fetching from API...")

            # Fetch data from API and store it
            result = get_swell_data(latitude, longitude)
            if not result:
                return jsonify({'success': False, 'message': 'Failed to fetch or store data from API.'})

            # After the data is inserted, commit the transaction to save the changes
            connection.commit()  # Ensure data is committed after insertion

            # Re-fetch the location ID after inserting new data
            cursor.execute('''SELECT location_id FROM locations
                            WHERE latitude = CAST(%s AS DECIMAL(10, 7))
                            AND longitude = CAST(%s AS DECIMAL(10, 7))''',
                        (latitude, longitude))
            location = cursor.fetchone() 


        # Handle the case where the location ID is still not found
        if not location:
            print("[ERROR] Location insertion or retrieval failed.")
            return jsonify({'success': False, 'message': 'Location insertion failed.'})

        # Extract the location ID
        location_id = location['location_id']
        print(f"[DEBUG] Found Location ID: {location_id}")

        # Fetch hourly swell data for the found location
        cursor.execute('''SELECT time, swell_wave_height
                          FROM hourly_swell
                          WHERE location_id = %s
                          ORDER BY time ASC''', (location_id,))
        hourly_data = cursor.fetchall()

        # Fetch current swell data for the found location
        cursor.execute('''SELECT * FROM current_swell
                          WHERE location_id = %s
                          ORDER BY time DESC LIMIT 1''', (location_id,))
        current_data = cursor.fetchone()

        # Check if the data is present
        if not hourly_data or not current_data:
            return jsonify({'success': False, 'message': 'No swell data found for this location.'})

        # Prepare response for the frontend
        response = {
            'success': True,
            'hourly': {
                'time': [row['time'].strftime('%Y-%m-%d %H:%M') for row in hourly_data],
                'swell_wave_height': [row['swell_wave_height'] for row in hourly_data]
            },
            'current': {
                'time': current_data['time'].strftime('%Y-%m-%d %H:%M'),
                'swell_wave_height': current_data['swell_wave_height'],
                'swell_wave_direction': current_data['swell_wave_direction'],
                'swell_wave_period': current_data['swell_wave_period']
            }
        }

    except Error as e:
        print(f"[ERROR] Database error: {e}")
        response = {'success': False, 'message': f'Database error: {str(e)}'}
    finally:
        # Ensure the database connection is closed
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

    print(f"[DEBUG] Response: {response}")
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
