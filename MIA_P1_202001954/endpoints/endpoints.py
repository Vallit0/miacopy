from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/informacion_estudiante', methods=['GET'])
def informacion_estudiante():
    estudiante = {
        "carnet": "202001954",
        "nombre": "Estuardo Valle"
    }
    return jsonify(estudiante)

if __name__ == '__main__':
    app.run(debug=True)
