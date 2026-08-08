from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'super_secret_key_sickleave'

def get_db():
    conn = sqlite3.connect('sick_leaves.db')
    conn.row_factory = sqlite3.Row
    return conn

# إنشاء الجدول عند التشغيل
with get_db() as conn:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_code TEXT UNIQUE,
            national_id TEXT,
            name_ar TEXT,
            name_en TEXT,
            duration TEXT,
            admission_date TEXT,
            discharge_date TEXT,
            issue_date TEXT,
            nationality TEXT,
            employer TEXT,
            practitioner_name TEXT,
            position TEXT
        )
    ''')

@app.route('/', methods=['GET', 'POST'])
def index():
    leave = None
    error = None
    if request.method == 'POST':
        service_code = request.form.get('service_code')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leaves WHERE service_code = ?", (service_code,))
        leave = cursor.fetchone()
        if not leave:
            error = "لم يتم العثور على إجازة مرضية بهذا الرقم"
    return render_template('index.html', leave=leave, error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == '123456':  # كلمة المرور
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            error = 'كلمة المرور غير صحيحة'
    return render_template('login.html', error=error)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    msg = None
    if request.method == 'POST':
        data = (
            request.form.get('service_code'),
            request.form.get('national_id'),
            request.form.get('name_ar'),
            request.form.get('name_en'),
            request.form.get('duration'),
            request.form.get('admission_date'),
            request.form.get('discharge_date'),
            request.form.get('issue_date'),
            request.form.get('nationality'),
            request.form.get('employer'),
            request.form.get('practitioner_name'),
            request.form.get('position')
        )
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO leaves (service_code, national_id, name_ar, name_en, duration, admission_date, discharge_date, issue_date, nationality, employer, practitioner_name, position)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', data)
            conn.commit()
            msg = "تم حفظ الإجازة المرضية بنجاح!"
        except Exception as e:
            msg = f"حدث خطأ أثناء الحفظ: {str(e)}"

    return render_template('admin.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
