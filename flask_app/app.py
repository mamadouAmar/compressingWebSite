from flask import Flask, render_template, request
import compression



app = Flask(__name__)


@app.route('/')
def index():       
    return render_template('index.html')


@app.route('/resultat',methods = ['POST'])
def resultat():
    results = request.files
    filename = results['myFile']
    fileCompressed, b = compression.compress(filename, 0, 2, 0, 1000, 1000, True, True)
    return render_template('index.html', fileCompressed)