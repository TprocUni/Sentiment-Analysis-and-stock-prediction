#Flask server environment
from flask import Flask, render_template, request, jsonify
import json
import os

#app = Flask(__name__)

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
graphData = None  # Add a global variable to store the graph data

FLASK_SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(FLASK_SERVER_DIR)
#PARENT_DIR = os.path.dirname(ROOT_DIR)  # Get the parent directory of ROOT_DIR
CONFIG_FILE_PATH = os.path.join(ROOT_DIR, 'config.json')
#print(CONFIG_FILE_PATH)



'''
PARENT_DIR = os.path.dirname(ROOT_DIR)  # Get the parent directory of ROOT_DIR

FLASK_SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(FLASK_SERVER_DIR)
CONFIG_DIR = os.path.join(ROOT_DIR, 'FinalPythonCode')  # Add the 'FinalPythonCode' directory
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR, 'config.json')
'''

@app.route('/')
def index():
    return render_template('graph.html')


@app.route('/update-graph', methods=['POST'])
def updateGraph():
    global graphData
    incomingData = request.get_json()
    if incomingData:
        graphData = incomingData
        print("success")
        return jsonify({'status': 'success'})
    else:
        print("big fail")
        return jsonify({'status': 'error'}), 400


@app.route('/get-graph', methods=['POST'])
def getGraph():
    global graphData
    if graphData:
        print("success")
        return jsonify(graphData)
    else:
        print("big fail")
        return jsonify({'status': 'error'}), 400


@app.route('/update-threshold', methods=['POST'])
def update_threshold():
    threshold = request.get_json().get('threshold', None)
    if threshold is not None:
        with open(CONFIG_FILE_PATH, 'r') as f:
            config_data = json.load(f)

        config_data['THRESHOLD'] = float(threshold)

        with open(CONFIG_FILE_PATH, 'w') as f:
            json.dump(config_data, f)

        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error'}), 400


if __name__ == '__main__':
    app.run(debug=False)
