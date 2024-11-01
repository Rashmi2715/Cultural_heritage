import mysql.connector

# Connect to MySQL
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Rashmi@123',
    database='your_database'
)

cursor = connection.cursor()

# Function to convert image to binary
def convert_to_binary(filename):
    with open(filename, 'rb') as file:
        binary_data = file.read()
    return binary_data

# SQL query
sql_query = """INSERT INTO cultural_artifacts_images (Cul_id, Name, Image) 
               VALUES (%s, %s, %s)"""

# Image paths
image_data = [
    (1, 'Taj Mahal', convert_to_binary('/path/to/taj_mahal_image.jpg')),
    (1, 'Fatehpur Sikri', convert_to_binary('/path/to/fatehpur_sikri_image.jpg')),
    (1, 'Agra Fort', convert_to_binary('/path/to/agra_fort_image.jpg')),
    (1, 'Akbar\'s Tomb', convert_to_binary('/path/to/akbars_tomb_image.jpg')),
    (1, 'Itimad-ud-Daula\'s Tomb', convert_to_binary('/path/to/itimad_udaula_tomb_image.jpg'))
]

# Execute the query for each image
cursor.executemany(sql_query, image_data)

# Commit the transaction
connection.commit()

# Close the connection
cursor.close()
connection.close()
