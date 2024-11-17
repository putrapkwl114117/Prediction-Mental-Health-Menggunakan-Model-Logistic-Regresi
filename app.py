from flask import Flask, render_template, request, flash, redirect, url_for
import pickle
import numpy as np
from database import save_to_database, get_statistics
import re

app = Flask(__name__)
app.secret_key = 'berkah_abadi2024'

with open('models/model_stres_level.pkl', 'rb') as file:
    model = pickle.load(file)

# Fungsi untuk memvalidasi input
def is_valid_input(data):
    try:
        data = [float(item) if item != '' else None for item in data]
    except ValueError:
        return False
    return True


def sanitize_input(input_string):
    if input_string is None:
        return ''
    return re.sub(r'<[^>]*>', '', input_string) 

# Validasi format data untuk memastikan semuanya valid
def validate_input(data):
    for item in data:
        if item == '' or item is None:
            return False
        try:
            float(item)
        except ValueError:
            return False
    return True

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = [
            sanitize_input(request.form.get('anxiety_level')),
            sanitize_input(request.form.get('self_esteem')),
            1 if sanitize_input(request.form.get('mental_health_history')).lower() == 'ya' else 0,
            sanitize_input(request.form.get('depression')),
            sanitize_input(request.form.get('headache')),
            sanitize_input(request.form.get('blood_pressure')),
            sanitize_input(request.form.get('sleep_quality')),
            sanitize_input(request.form.get('quest8')),
            sanitize_input(request.form.get('noise_level')),
            sanitize_input(request.form.get('safety')),
            sanitize_input(request.form.get('quest11')),
            sanitize_input(request.form.get('quest12')),
            sanitize_input(request.form.get('academic_performance')),
            sanitize_input(request.form.get('study_load')),
            sanitize_input(request.form.get('relationship_with_supervisor')),
            sanitize_input(request.form.get('quest17')),
            sanitize_input(request.form.get('work_load')),
            sanitize_input(request.form.get('quest19')),
            sanitize_input(request.form.get('extracurricular_activity')),
            sanitize_input(request.form.get('quest21')),
        ]

        
        print(data)

        if not validate_input(data):
            flash('Semua inputan harus diisi dengan benar. Periksa kembali inputan kamu.', 'danger')
            return redirect(url_for('screening'))
        
        if any(item is None or item == '' for item in data):
            flash('Semua inputan harus diisi. Periksa kembali inputan kamu.', 'danger') 
            return redirect(url_for('screening'))

        if not is_valid_input(data):
            flash('Input yang Anda masukkan tidak valid. Periksa kembali inputan Anda.', 'danger')
            return redirect(url_for('screening'))

        try:
            data = np.array(data, dtype=float).reshape(1, -1)
            prediction = model.predict(data)[0] 
        
            save_to_database(data.flatten().tolist(), prediction)

            # Flash pesan berdasarkan level stres
            if prediction == 0:
                flash({
                    'level': 0,
                    'message': 'Kamu tuh level chill banget, kayak kamu lagi santai nggak ada beban, semua terkendali, dan pikiran rasanya damai banget!',
                    'image': 'level0.png'
                }, 'prediction')
            elif prediction == 1:
                flash({
                    'level': 1,
                    'message': 'Nah, di level ini tuh mulai ada sedikit tekanan. Nggak terlalu berat sih, masih bisa di-handle sambil jalan, tapi udah mulai terasa ada yang ngganjel dikit.',
                    'image': 'level1.png'
                }, 'prediction')
            elif prediction == 2:
                flash({
                    'level': 2,
                    'message': 'Kalau udah sampai sini, kamu mulai ngerasa agak tegang dan kepikiran terus. Belum parah, tapi udah mulai butuh perhatian biar nggak makin berat.',
                    'image': 'level2.png'
                }, 'prediction')
            else:
                flash('Hasil prediksi tidak diketahui. Silakan coba lagi.', 'danger')

            return redirect(url_for('screening'))
        except Exception as e:
            flash('Terjadi kesalahan saat memproses data. Silakan coba lagi.', 'danger')
            return redirect(url_for('screening'))
        
    stats = get_statistics()
    return render_template('index.html', stats=stats)

@app.route('/screening')
def screening():
    return render_template('screening.html')

if __name__ == '__main__':
    app.run(debug=True)
