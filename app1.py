import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import mysql.connector
from db_connection import get_connection

# Function to register a student and update the combobox
def register_student():
    name = name_entry.get()
    email = email_entry.get()
    
    if not name or not email:
        messagebox.showerror("Input Error", "Please fill in all fields.")
        return
    
    try:
        # Register the student in the database
        connection = get_connection()
        cursor = connection.cursor()

        # Insert student data into the 'students' table
        cursor.execute("INSERT INTO students (name, email) VALUES (%s, %s)", (name, email))
        connection.commit()

        # Close the cursor after insert
        cursor.close()

        # Refresh the student combobox
        update_student_combobox()

        # Clear the input fields
        name_entry.delete(0, tk.END)
        email_entry.delete(0, tk.END)

        messagebox.showinfo("Success", "Student registered successfully!")

        connection.close()
        
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error occurred: {err}")

# Function to update student combobox after a new student is registered
def update_student_combobox():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Fetch all students from the 'students' table
        cursor.execute("SELECT student_id, name FROM students")
        students = cursor.fetchall()

        # If students are found, update the combobox
        if students:
            student_id_combobox['values'] = [f"{student[0]} - {student[1]}" for student in students]
        else:
            messagebox.showwarning("No Students", "No students found in the database.")
        
        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error occurred: {err}")

# Function to register a course for the selected student
def register_course():
    selected_student = student_id_combobox.get()
    selected_course = course_id_combobox.get()
    
    if not selected_student or not selected_course:
        messagebox.showerror("Input Error", "Please select a student and a course.")
        return

    # Extract student_id and course_id from the selected text in the comboboxes
    student_id = selected_student.split(" - ")[0]
    course_id = selected_course.split(" - ")[0]

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Check if student and course exist
        cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
        student_exists = cursor.fetchone()

        cursor.execute("SELECT * FROM courses WHERE course_id = %s", (course_id,))
        course_exists = cursor.fetchone()

        if not student_exists or not course_exists:
            messagebox.showerror("Invalid Data", "Either the student or the course does not exist.")
            cursor.close()
            connection.close()
            return

        # Insert into the registrations table
        cursor.execute("INSERT INTO registrations (student_id, course_id) VALUES (%s, %s)", (student_id, course_id))
        connection.commit()

        messagebox.showinfo("Success", "Course registered successfully!")

        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error occurred: {err}")

# Function to load students and courses into comboboxes at the start
def load_data():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Load courses into combobox
        cursor.execute("SELECT course_id, course_name FROM courses")
        courses = cursor.fetchall()

        if courses:
            course_id_combobox['values'] = [f"{course[0]} - {course[1]}" for course in courses]
        else:
            # Insert sample courses if no courses are available
            insert_courses()

        cursor.close()
        connection.close()

        # Refresh the student combobox
        update_student_combobox()

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error occurred: {err}")

# Function to insert sample courses into the courses table if not already inserted
def insert_courses():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Insert sample courses into the 'courses' table
        courses = [
            ('Mathematics'),
            ('Computer Science'),
            ('Physics'),
            ('Chemistry'),
            ('Biology')
        ]
        for course in courses:
            cursor.execute("INSERT INTO courses (course_name) VALUES (%s)", (course,))
        
        connection.commit()
        cursor.close()
        connection.close()

        # Reload courses data to refresh the combobox after inserting courses
        load_data()

        messagebox.showinfo("Courses Inserted", "Sample courses have been inserted successfully.")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error occurred while inserting courses: {err}")

# Function to view students with courses
def view_students_with_courses():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Query to fetch student names and their courses
        cursor.execute("""
            SELECT s.name AS student_name, c.course_name
            FROM registrations r
            JOIN students s ON r.student_id = s.student_id
            JOIN courses c ON r.course_id = c.course_id
        """)
        students_with_courses = cursor.fetchall()

        # Open a new window to display the data
        view_window = tk.Toplevel(root)
        view_window.title("Students with Courses")

        # Create a Treeview to display the data in a tabular form
        tree = ttk.Treeview(view_window, columns=("Student Name", "Course Name"), show="headings")
        tree.heading("Student Name", text="Student Name")
        tree.heading("Course Name", text="Course Name")

        # Insert data into the Treeview
        for student in students_with_courses:
            tree.insert("", "end", values=student)

        tree.pack(padx=10, pady=10)

        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error occurred: {err}")

# Tkinter GUI setup
root = tk.Tk()
root.title("Student Course Registration System")

# Register Student UI
register_frame = tk.Frame(root)
register_frame.pack(padx=10, pady=10)

tk.Label(register_frame, text="Student Name").grid(row=0, column=0, pady=5)
name_entry = tk.Entry(register_frame)
name_entry.grid(row=0, column=1, pady=5)

tk.Label(register_frame, text="Student Email").grid(row=1, column=0, pady=5)
email_entry = tk.Entry(register_frame)
email_entry.grid(row=1, column=1, pady=5)

register_button = tk.Button(register_frame, text="Register Student", command=register_student)
register_button.grid(row=2, columnspan=2, pady=10)

# Register for Course UI
course_register_frame = tk.Frame(root)
course_register_frame.pack(padx=10, pady=10)

tk.Label(course_register_frame, text="Select Student").grid(row=0, column=0, pady=5)
student_id_combobox = ttk.Combobox(course_register_frame)
student_id_combobox.grid(row=0, column=1, pady=5)

tk.Label(course_register_frame, text="Select Course").grid(row=1, column=0, pady=5)
course_id_combobox = ttk.Combobox(course_register_frame)
course_id_combobox.grid(row=1, column=1, pady=5)

course_register_button = tk.Button(course_register_frame, text="Register for Course", command=register_course)
course_register_button.grid(row=2, columnspan=2, pady=10)

# View Students with Courses UI
view_button = tk.Button(root, text="View Students with Courses", command=view_students_with_courses)
view_button.pack(pady=20)

# Load data into comboboxes when the program starts
load_data()

# Run the Tkinter event loop
root.mainloop()
