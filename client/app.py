import os
from flask import Flask
from flask import render_template
from flask import request
from instance.scripts.analysis import start

app = Flask(__name__)

uploads_dir = os.path.join(app.instance_path, 'scripts')

app.config['FLASK_APP'] = 'app'
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.config['TESTING'] = True

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/get_data', methods=['POST'])
def get_data():
    dataFile = request.files['file_path']
    dataFileName = dataFile.filename
    dataFile.save(os.path.join(uploads_dir, dataFileName))

    if "csv" in dataFileName:
        fileType = "csv"
    
    if "json" in dataFileName:
        fileType = "json"

    filePath = 'scripts/' + dataFileName
    result = start(os.path.join(app.instance_path, filePath), fileType)

    print(result)
    return render_template('analysis.html')
    
if __name__ == "__main__":
    app.run(debug=True)