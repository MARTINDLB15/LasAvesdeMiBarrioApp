import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import get_connection, init_db
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'admin123'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'static/uploads'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Inicializamos la base de datos al arrancar la app
init_db()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre_completo = request.form.get('nombre_completo')
        nombre_comun = request.form.get('nombre_comun')
        nombre_cientifico = request.form.get('nombre_cientifico')
        comentario = request.form.get('comentario')
        imagen = request.files.get('imagen')

        ruta_imagen = None
        if imagen and allowed_file(imagen.filename):
            nombre_archivo = secure_filename(imagen.filename)
            ruta_absoluta = os.path.join(UPLOAD_FOLDER, nombre_archivo)
            imagen.save(ruta_absoluta)
            ruta_imagen = f'uploads/{nombre_archivo}'

        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO registros (nombre_completo, nombre_comun, nombre_cientifico, comentario, imagen, estado)
                VALUES (?, ?, ?, ?, ?, 'pendiente')
            ''', (nombre_completo, nombre_comun, nombre_cientifico, comentario, ruta_imagen))
            conn.commit()

        return redirect(url_for('explora'))

    return render_template('registro.html')

@app.route('/explora')
def explora():
    with get_connection() as conn:
        cur = conn.cursor()
        if session.get('usuario') == 'admin':
            cur.execute("SELECT * FROM registros")
            registros = cur.fetchall()

            cur.execute("SELECT COUNT(*) FROM registros WHERE estado='aprobado'")
            total_aprobados = cur.fetchone()[0]

            return render_template('explora.html', registros=registros, total_aprobados=total_aprobados)
        else:
            cur.execute("SELECT * FROM registros WHERE estado='aprobado'")
            registros = cur.fetchall()
            return render_template('explora.html', registros=registros)

@app.route('/eliminar/<int:registro_id>', methods=['POST'])
def eliminar(registro_id):
    if session.get('usuario') != 'admin':
        flash("No autorizado", "error")
        return redirect(url_for('explora'))

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM registros WHERE id=?", (registro_id,))
        conn.commit()

    return redirect(url_for('explora'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'admin123':
            session['usuario'] = 'admin'
            return redirect(url_for('index'))
        else:
            flash('Contraseña incorrecta', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))

@app.route('/admin_registros', methods=['GET', 'POST'])
def admin_registros():
    if session.get('usuario') != 'admin':
        return redirect(url_for('login'))

    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("SELECT * FROM registros WHERE estado='pendiente'")
        pendientes = cur.fetchall()

        cur.execute("SELECT * FROM registros WHERE estado='aprobado'")
        aprobados = cur.fetchall()



    return render_template('admin_registros.html', pendientes=pendientes, aprobados=aprobados)

@app.route('/aprobar/<int:registro_id>', methods=['POST'])
def aprobar(registro_id):
    if session.get('usuario') != 'admin':
        return redirect(url_for('login'))

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE registros SET estado='aprobado' WHERE id=?", (registro_id,))
        conn.commit()

    return redirect(url_for('admin_registros'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)