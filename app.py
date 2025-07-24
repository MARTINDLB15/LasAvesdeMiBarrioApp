from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    return render_template ('index.html')

@app.route('/guia')
def guia():
    return render_template ('guia.html')

@app.route('/registro')
def registro():
    return render_template ('registro.html')

@app.route('/explora')
def explora():
    return render_template ('explora.html')

@app.route('/conoce')
def conoce():
    return render_template ('conoce.html')

if __name__ == '__main__':
    app.run(debug=True)