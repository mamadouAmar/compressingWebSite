from flask import Flask, render_template, request, make_response
import compression



app = Flask(__name__)


@app.route('/')
def index():       
    return render_template('index.html')


@app.route('/resultat',methods = ['POST'])
def resultat():
    results = request.files
    filename = results['myFile']
    fileCompressed, b = compression.compress(filename, 0, 2, 0, 1000, 1000, False, False)
    response = make_response(fileCompressed)
    response.headers["Content-type"] = "application/wav"
    response.headers["Content-Disposition"] = "attachment; filename=compressed.wav"
    return response