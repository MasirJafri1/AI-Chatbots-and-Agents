from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import os
import sqlite3
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt + "\n" + question)
    return response.text

def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    return rows

prompt = """
You are an expert in converting English questions into SQL queries!\n
The SQL database has a table named STUDENT and has the following columns: NAME, CLASS, SELECTION, MARKS.\n
For example:\n
Example 1:\n
Question: How many student records are present?\n
SQL: SELECT COUNT(*) FROM STUDENT;\n
Example 2:\n
Question: Show me all the students in the Science section.\n
SQL: SELECT * FROM STUDENT WHERE SELECTION = "Science";\n
Example 3:\n
Question: Give me the names of students who scored more than 80 marks.\n
SQL: SELECT NAME FROM STUDENT WHERE MARKS > 80;\n
Rules:\n
- Only output the SQL query.\n
- Do NOT include the words "SQL", "code", backticks, or any explanations.\n
- Do NOT add anything before or after the SQL query.
"""

st.set_page_config(page_title="Text to SQL LLM App")
st.header("Gemini App to retrieve Text to SQL Data")

question = st.text_input("Input:", key="input")
submit = st.button("Ask the question")

if submit:
    response = get_gemini_response(question, prompt)
    data = read_sql_query(response, "student.db")

    st.subheader("Generated SQL Query:")
    st.code(response)

    st.subheader("Database Output:")
    for row in data:
        st.header(row)
