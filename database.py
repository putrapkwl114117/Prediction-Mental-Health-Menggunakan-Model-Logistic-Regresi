import mysql.connector
from mysql.connector import Error
import numpy as np

# Fungsi untuk menyimpan hasil ke database
def save_to_database(data, prediction):
    connection = None  
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='berkah_abadi',
            user='root',
            password=''
        )
        if connection.is_connected():
            cursor = connection.cursor()

            data = [int(x) if isinstance(x, np.integer) else float(x) if isinstance(x, np.floating) else x for x in data]
            prediction = int(prediction) if isinstance(prediction, np.integer) else prediction
            
            query = """INSERT INTO screening_results (
                     anxiety_level, self_esteem, mental_health_history,
                     depression, headache, blood_pressure, sleep_quality, quest8, noise_level, safety, quest11, quest12, academic_performance,
                     study_load, work_load, relationship_with_supervisor, quest17,
                     quest19, extracurricular_activity, quest21, stress_zone)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, data + [prediction])
            connection.commit()
    except Error as e:
        print("Error:", e)
    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()

# Fungsi untuk mengambil statistik zona stres dengan persentase
def get_statistics():
    connection = None
    statistics = {"Zona Tenang": 0, "Zona Stres Ringan": 0, "Zona Tanda Awal": 0}
    total_respondents = 0 
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='berkah_abadi',
            user='root',
            password=''
        )
        if connection.is_connected():
            cursor = connection.cursor()
            query = "SELECT stress_zone, COUNT(*) FROM screening_results GROUP BY stress_zone"
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Mapping hasil ke dalam dictionary dan hitung total responden
            for zone, count in results:
                if zone == 0:
                    statistics["Zona Tenang"] = count
                elif zone == 1:
                    statistics["Zona Stres Ringan"] = count
                elif zone == 2:
                    statistics["Zona Tanda Awal"] = count
                total_respondents += count  

            # Hitung persentase setiap zona stres
            if total_respondents > 0:
                statistics["Zona Tenang"] = (statistics["Zona Tenang"] / total_respondents) * 100
                statistics["Zona Stres Ringan"] = (statistics["Zona Stres Ringan"] / total_respondents) * 100
                statistics["Zona Tanda Awal"] = (statistics["Zona Tanda Awal"] / total_respondents) * 100

    except Error as e:
        print("Error:", e)
    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()

    return statistics
