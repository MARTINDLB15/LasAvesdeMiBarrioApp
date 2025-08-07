import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, flash

from werkzeug.utils import secure_filename 

app = Flask(__name__)
app.secret_key = 'admin123'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'static/uploads'
REGISTROS_FILE = 'registros.json'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def cargar_registros(archivo=REGISTROS_FILE):
    if os.path.exists(archivo):
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def guardar_registros(lista, archivo=REGISTROS_FILE):
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)

@app.route('/')
@app.route('/index')
def index():
    return render_template ('index.html')

@app.route('/registro',  methods=['GET', 'POST'])
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

        nuevo_registro = {
            'nombre_completo': nombre_completo,
            'nombre_comun': nombre_comun,
            'nombre_cientifico': nombre_cientifico,
            'comentario': comentario,
            'imagen': ruta_imagen
        }

        pendientes = cargar_registros('pendientes.json')
        pendientes.append(nuevo_registro)
        guardar_registros(pendientes, 'pendientes.json')

        return redirect(url_for('explora'))

    return render_template ('registro.html')

@app.route('/explora')
def explora():
    registros_aprobados = cargar_registros('aprobados.json')
    
    if session.get('usuario') == 'admin':
        registros_pendientes = cargar_registros('pendientes.json')
        registros = registros_aprobados + registros_pendientes
        return render_template('explora.html',
                               registros=registros,
                               total_aprobados=len(registros_aprobados))
    else:
        return render_template('explora.html', registros=registros_aprobados)

@app.route('/eliminar/<int:indice>', methods=['POST'])
def eliminar(indice):
    if session.get('usuario') != 'admin':
        flash("No autorizado", "error")
        return redirect(url_for('explora'))

    registros = cargar_registros('aprobados.json')
    if 0 <= indice < len(registros):
        registros.pop(indice)
        guardar_registros(registros, 'aprobados.json')

    return redirect(url_for('explora'))
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'admin123':  # Cambia esta contraseña
            session['usuario'] = 'admin'
            return redirect(url_for('index'))  # Cambia a la ruta principal de tu app
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

    pendientes = cargar_registros('pendientes.json')
    aprobados = cargar_registros('aprobados.json')

    if request.method == 'POST':
        indice = int(request.form.get('indice'))
        registro_aprobado = pendientes.pop(indice)
        aprobados.append(registro_aprobado)

        guardar_registros(pendientes, 'pendientes.json')
        guardar_registros(aprobados, 'aprobados.json')
        return redirect(url_for('admin_registros'))

    return render_template('admin_registros.html', pendientes=pendientes)

@app.route('/aprobar/<int:indice>', methods=['POST'])
def aprobar(indice):
    if session.get('usuario') != 'admin':
        return redirect(url_for('login'))

    pendientes = cargar_registros('pendientes.json')
    aprobados = cargar_registros('aprobados.json')

    if 0 <= indice < len(pendientes):
        registro = pendientes.pop(indice)
        aprobados.append(registro)
        guardar_registros(pendientes, 'pendientes.json')
        guardar_registros(aprobados, 'aprobados.json')

    return redirect(url_for('admin_registros'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)