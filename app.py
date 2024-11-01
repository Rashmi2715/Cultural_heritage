from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database connection
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Rashmi@123',  # Change this to your actual MySQL password
        database='cultural_heritage'  # Ensure this database exists and has relevant data
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
                return redirect(url_for('login'))

        except Error as e:
            flash("An error occurred while connecting to the database.", "error")
            return redirect(url_for('login'))

        finally:
            cursor.close()
            connection.close()

    return render_template('login.html')

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

        except Error as e:
            if e.errno == 1062:  # MySQL error code for duplicate entry
                flash("Username already exists. Please choose a different username.", "error")
            else:
                flash("An error occurred during sign-up. Please try again.", "error")
            return redirect(url_for('signup'))

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

    query = "SELECT * FROM cultural_place WHERE name LIKE %s"
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

    query = "SELECT * FROM cultural_place WHERE name = %s"
    cursor.execute(query, (place_name,))
    place = cursor.fetchone()

    cursor.close()
    connection.close()

    if place:
        return render_template('place_detail.html', place=place)
    else:
        return "Place not found", 404

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
