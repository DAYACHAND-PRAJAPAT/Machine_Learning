from flask import Flask, render_template, request
import joblib
import mysql.connector
import numpy as np

app = Flask(__name__)
model = joblib.load('diabities.lb')

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Daya@123",
        database="diabetes_prediction"
    )

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/project')
def project():
    return render_template('project.html')

@app.route('/history')
def history():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM DiabetesHistory ORDER BY id DESC")
        history_data = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('history.html', history_data=history_data)
    except Exception as e:
        print("History error:", e)
        return render_template('history.html', history_data=[])

@app.route('/predict', methods=['POST'])
def predict():
    try:
        features = [
            float(request.form['preg']),
            float(request.form['plas']),
            float(request.form['pres']),
            float(request.form['skin']),
            float(request.form['insu']),
            float(request.form['mass']),
            float(request.form['pedi']),
            float(request.form['age'])
        ]

        prediction = model.predict([features])[0]
        result = "Diabetic" if prediction == 1 else "Not Diabetic"

        conn = get_db_connection()
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO DiabetesHistory
            (preg, plas, pres, skin, insu, mass, pedi, age, result)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (*features, result))
        conn.commit()
        cursor.close()
        conn.close()

        return render_template('project.html', prediction=result)
    except Exception as e:
        return render_template('project.html', prediction=f"Error: {e}")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
