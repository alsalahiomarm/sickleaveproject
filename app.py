from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

# إنشاء قاعدة البيانات والجدول تلقائياً
def init_db():
    conn = sqlite3.connect(app.config['DB_NAME'])
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_code TEXT UNIQUE NOT NULL,
            national_id TEXT NOT NULL,
            full_name TEXT NOT NULL,
            issue_date TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            doctor_name TEXT NOT NULL,
            doctor_title TEXT DEFAULT 'استشاري'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

# صفحة تسجيل الدخول للوحة التحكم
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error="كلمة المرور غير صحيحة!")
    return render_template('login.html')

# تسجيل الخروج
@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin_login'))

# لوحة التحكم - محمية بالكامل
@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin.html')

# API للاستعلام عن التقرير
@app.route('/api/verify', methods=['GET'])
def verify_report():
    service_code = request.args.get('code', '').strip()
    national_id = request.args.get('id', '').strip()

    conn = sqlite3.connect(app.config['DB_NAME'])
    cursor = conn.cursor()
    cursor.execute('''
        SELECT full_name, issue_date, start_date, end_date, doctor_name, doctor_title 
        FROM reports 
        WHERE service_code = ? AND national_id = ?
    ''', (service_code, national_id))
    
    report = cursor.fetchone()
    conn.close()

    if report:
        return jsonify({
            'success': True,
            'report': {
                'full_name': report[0],
                'issue_date': report[1],
                'start_date': report[2],
                'end_date': report[3],
                'doctor_name': report[4],
                'doctor_title': report[5]
            }
        })
    else:
        return jsonify({'success': False, 'message': 'لم يتم العثور على التقرير'})

# API لإضافة تقرير جديد
@app.route('/api/reports/add', methods=['POST'])
def add_report():
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'غير مسموح بالوصول'}), 403

    data = request.json
    service_code = data.get('service_code') or f"GSL{data.get('national_id')[:4]}1258"
    national_id = data.get('national_id')
    full_name = data.get('full_name')
    issue_date = data.get('issue_date')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    doctor_name = data.get('doctor_name', 'سامي هليل الحربي')
    doctor_title = data.get('doctor_title', 'استشاري')

    try:
        conn = sqlite3.connect(app.config['DB_NAME'])
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reports (service_code, national_id, full_name, issue_date, start_date, end_date, doctor_name, doctor_title)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (service_code, national_id, full_name, issue_date, start_date, end_date, doctor_name, doctor_title))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'service_code': service_code})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'رمز الخدمة مستخدم من قبل'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)