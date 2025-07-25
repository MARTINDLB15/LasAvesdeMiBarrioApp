import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename 

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
@app.route('/index')
def index():
    return render_template ('index.html')

@app.route('/guia')
def guia():
    return render_template ('guia.html')

lista_registros = []
@app.route('/registro',  methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre_completo = request.form.get('nombre_completo')
        nombre_comun = request.form.get('nombre_comun')
        nombre_cientifico = request.form.get('nombre_cientifico')
        comentario = request.form.get('comentario')
        imagen = request.files.get('imagen')

        ruta_imagen = None
        if imagen and imagen.filename != '':
            nombre_archivo = imagen.filename
            ruta_absoluta = os.path.join(UPLOAD_FOLDER, nombre_archivo)
            imagen.save(ruta_absoluta)
            ruta_imagen = f'uploads/{nombre_archivo}'
        
        lista_registros.append({
            'nombre_completo': nombre_completo,
            'nombre_comun': nombre_comun,
            'nombre_cientifico': nombre_cientifico,
            'comentario': comentario,
            'imagen': ruta_imagen
        })
        return redirect(url_for('explora'))

    return render_template ('registro.html')

@app.route('/explora')
def explora():
    return render_template ('explora.html', registros=lista_registros)

@app.route('/conoce')
def conoce():
    return render_template ('conoce.html')

@app.route('/eliminar/<int:indice>', methods=['POST'])
def eliminar(indice):
    if 0 <= indice < len(lista_registros):
        del lista_registros[indice]
    return redirect(url_for('explora'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)