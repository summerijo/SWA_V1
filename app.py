from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
from api_routes import api

app = Flask(__name__)
app.secret_key = 'dev' 

# Register the Blueprint for API routes
app.register_blueprint(api)

# MySQL configuration
db_config = {
    'host': 'localhost',
    'user': 'root',      
    'password': 'root_123',
    'database': 'swa_db'
}

# Helper function to connect to the database
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

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
            return redirect(url_for('list_users'))
        
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
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Query to find the user by email
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()

        # If user exists and the password matches
        if user and user['password'] == password:
            session['email'] = email  # Store email in session
            return redirect(url_for('maps'))  # Redirect to maps.html on successful login
        else:
            return 'Invalid credentials, please try again.'  # Invalid credentials
    return render_template('login.html')


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
        return redirect(url_for('login'))  # Redirect to login if not logged in

if __name__ == '__main__':
    app.run(debug=True)
