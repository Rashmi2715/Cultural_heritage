from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database connection
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Rashmi@123',  # Replace with your actual MySQL password
        database='cultural_heritage'  # Make sure this database exists
    )
    return connection

# Home route
@app.route('/')
def index():
    return render_template('home.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM user WHERE Username = %s AND Password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            if user:
                session['username'] = user['Username']
                flash("Login successful!", "success")
                return redirect(url_for('index'))
            else:
                flash("Invalid username or password. Please try again.", "error")
        except Error as e:
            flash("An error occurred while connecting to the database.", "error")
        finally:
            cursor.close()
            connection.close()
    return render_template('login.html')
# Forgot Password route
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash("Passwords do not match. Please try again.", "error")
            return redirect(url_for('forgot_password'))
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Verify if the username exists
            cursor.execute("SELECT * FROM user WHERE Username = %s", (username,))
            user = cursor.fetchone()
            
            if user:
                # Update the password
                update_query = "UPDATE user SET Password = %s WHERE Username = %s"
                cursor.execute(update_query, (new_password, username))
                connection.commit()
                
                flash("Password updated successfully! Please login with your new password.", "success")
                return redirect(url_for('login'))
            else:
                flash("Username not found. Please try again.", "error")
        
        except Error as e:
            flash("An error occurred while updating the password. Please try again.", "error")
        
        finally:
            cursor.close()
            connection.close()
    
    return render_template('forgot_password.html')
# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        if password != confirm_password:
            flash("Passwords do not match. Please try again.", "error")
            return redirect(url_for('signup'))
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            query = "INSERT INTO user (Username, Email, Password) VALUES (%s, %s, %s)"
            cursor.execute(query, (username, email, password))
            connection.commit()

            flash("Account created successfully! Please login.", "success")
            return redirect(url_for('login'))
        
        except mysql.connector.Error as e:
            if e.errno == 1644:  # Error code for the trigger SIGNAL SQLSTATE '45000'
                flash(e.msg, "error")  # Flash the custom message from the trigger
            else:
                flash("An error occurred during sign-up. Please try again.", "error")
        
        finally:
            cursor.close()
            connection.close()
    
    return render_template('signup.html')


# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

# Search route (requires login)
@app.route('/search', methods=['POST'])
def search():
    if 'username' not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for('login'))
    search_term = request.form['search_term']
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM cultural_place WHERE Name LIKE %s"
    cursor.execute(query, ('%' + search_term + '%',))
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('search.html', places=results, search_term=search_term)

# Place detail route (requires login)
@app.route('/place/<string:place_name>')
def place_detail(place_name):
    if 'username' not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for('login'))
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM cultural_place WHERE Name = %s"
    cursor.execute(query, (place_name,))
    place = cursor.fetchone()
    cursor.close()
    connection.close()
    return render_template('place_detail.html', place=place) if place else ("Place not found", 404)

# Events route using stored procedure
@app.route('/place/<string:place_name>/events')
def events(place_name):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.callproc('GetEventsByPlace', [place_name])
        events = [row for result in cursor.stored_results() for row in result.fetchall()]
    except Error as e:
        print(f"Error: {e}")
        events = []
    finally:
        cursor.close()
        connection.close()
    return render_template('events.html', events=events, place={'name': place_name})

# Organizations route using stored procedure
@app.route('/place/<string:place_name>/organizations')
def organizations(place_name):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.callproc('GetOrganizationsByPlace', [place_name])
        organizations = [row for result in cursor.stored_results() for row in result.fetchall()]
    except Error as e:
        print(f"Error: {e}")
        organizations = []
    finally:
        cursor.close()
        connection.close()
    return render_template('organizations.html', organizations=organizations, place={'name': place_name})

# Famous Food route using stored procedure
@app.route('/place/<string:place_name>/famous_food')
def famous_food(place_name):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        # Call the GetFamousFoodByPlace function to get food details
        cursor.callproc('GetFamousFoodByPlace', [place_name])
        foods = [row for result in cursor.stored_results() for row in result.fetchall()]
        
        # Call the GetFamousFoodImagesByPlace function to get images
        cursor.execute(f"SELECT GetFamousFoodImagesByPlace(%s) AS Images", (place_name,))
        images_result = cursor.fetchone()
        images = images_result['Images'] if images_result else '[]'
        
    except Error as e:
        print(f"Error: {e}")
        foods = []
        images = '[]'
    
    finally:
        cursor.close()
        connection.close()
    
    # Convert the JSON result to a Python list
    image_list = json.loads(images) if images else []
    
    # Create a dictionary of food items with their corresponding images
    for food in foods:
        food['images'] = [img for img in image_list if img.startswith(food['food_name'].replace(" ", "_"))]
    
    return render_template('famous_food.html', foods=foods, place={'name': place_name})


# Artifacts route using stored procedure
# Artifacts route using stored procedure
# Artifacts route using stored procedure and function
@app.route('/place/<string:place_name>/artifacts')
def artifacts(place_name):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        # Call the stored procedure to get artifact details
        cursor.callproc('ArtifactsByPlace', [place_name])
        artifacts = [row for result in cursor.stored_results() for row in result.fetchall()]
        
        # Fetching image filenames using the stored function
        for artifact in artifacts:
            cursor.execute("SELECT GetArtifactImages(%s) AS Images", (artifact['Name'],))
            image_list = cursor.fetchone()['Images']
            artifact['Images'] = image_list.split(',') if image_list else []  # Split images into a list
        
    except Error as e:
        print(f"Error: {e}")
        artifacts = []
    finally:
        cursor.close()
        connection.close()
    
    return render_template('artifacts.html', artifacts=artifacts, place={'name': place_name})


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
