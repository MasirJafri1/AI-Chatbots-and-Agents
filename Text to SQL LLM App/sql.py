import sqlite3

connection = sqlite3.connect("student.db")
cursor = connection.cursor()

# Create table safely (won't error if it already exists)
cursor.execute("""
CREATE TABLE IF NOT EXISTS STUDENT(
    NAME VARCHAR(25),
    CLASS VARCHAR(25),
    SELECTION VARCHAR(25),
    MARKS INT
);
""")

# Insert 20 records
records = [
    ("Alice", "10A", "Science", 88),
    ("Bob", "10B", "Commerce", 76),
    ("Charlie", "10A", "Arts", 92),
    ("Diana", "10C", "Science", 81),
    ("Ethan", "10B", "Commerce", 67),
    ("Fiona", "10A", "Science", 95),
    ("George", "10C", "Arts", 73),
    ("Hannah", "10B", "Science", 89),
    ("Ian", "10A", "Commerce", 54),
    ("Julia", "10C", "Arts", 78),
    ("Kevin", "10B", "Science", 84),
    ("Lily", "10A", "Commerce", 91),
    ("Mason", "10C", "Arts", 62),
    ("Nora", "10B", "Science", 88),
    ("Oliver", "10A", "Commerce", 72),
    ("Paula", "10C", "Science", 97),
    ("Quinn", "10A", "Arts", 69),
    ("Ryan", "10B", "Commerce", 83),
    ("Sophia", "10C", "Science", 90),
    ("Thomas", "10A", "Arts", 58)
]

cursor.executemany(
    "INSERT INTO STUDENT (NAME, CLASS, SELECTION, MARKS) VALUES (?, ?, ?, ?)",
    records
)

connection.commit()
connection.close()

print("20 records inserted successfully!")
