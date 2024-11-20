import mysql.connector

def get_connection():
    """Returns a connection to the MySQL database."""
    connection = mysql.connector.connect(
        host="localhost",  # Your MySQL server host
        user="root",       # Your MySQL username
        password="#Deepi26",       # Your MySQL password
        database="student_course_db"  # Your database name
    )
    return connection
