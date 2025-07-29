import os
import json
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename 

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

REGISTROS_FILE = 'registros.json'

def cargar_registros():
    if os.path.exists(REGISTROS_FILE):
        with open(REGISTROS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def guardar_registros(lista):
    with open(REGISTROS_FILE, 'w', encoding='utf-8') as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)

# Cargar registros al iniciar
lista_registros = cargar_registros()


@app.route('/')
@app.route('/index')
def index():
    return render_template ('index.html')

@app.route('/guia')
def guia():
    return render_template ('guia.html')

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

        lista_registros.append(nuevo_registro)
        guardar_registros(lista_registros)

        return redirect(url_for('explora'))

    return render_template ('registro.html')

@app.route('/explora')
def explora():
    registros = cargar_registros()
    return render_template('explora.html', registros=registros)

@app.route('/conoce')
def conoce():
    return render_template ('conoce.html')

@app.route('/eliminar/<int:indice>', methods=['POST'])
def eliminar(indice):
    registros = cargar_registros()
    if 0 <= indice < len(lista_registros):
        del lista_registros[indice]
        guardar_registros(lista_registros)
    return redirect(url_for('explora'))


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)