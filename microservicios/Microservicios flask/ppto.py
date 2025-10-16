from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

# Conexión a MongoDB
cliente_mongo = MongoClient("mongodb://localhost:27017/")
base_datos = cliente_mongo["finanzas"]
coleccion_presupuestos = base_datos["presupuestos"]

# Función para compatibilidad JSON
def convertir_a_json(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


@app.route("/")
def index():
    return "Microservicio de Presupuestos funcionando"


# Crear un presupuesto
@app.route("/presupuesto", methods=["POST"])
def crear_presupuesto():
    datos = request.get_json()

    if not datos or not datos.get("user_id") or not datos.get("ingreso_mensual") or not datos.get("gasto_maximo"):
        return jsonify({"mensaje": "Campos requeridos: user_id, ingreso_mensual, gasto_maximo"}), 400

    # Validar que no exista ya presupuesto para este user_id
    existente = coleccion_presupuestos.find_one({"user_id": datos["user_id"]})
    if existente:
        return jsonify({"mensaje": "Ya existe un presupuesto para este usuario"}), 400

    try:
        ingreso = float(datos["ingreso_mensual"])
        gasto = float(datos["gasto_maximo"])
    except Exception:
        return jsonify({"mensaje": "ingreso_mensual y gasto_maximo deben ser números"}), 400

    documento = {
        "user_id": datos["user_id"],
        "ingreso_mensual": ingreso,
        "gasto_maximo": gasto
    }

    resultado = coleccion_presupuestos.insert_one(documento)
    guardado = coleccion_presupuestos.find_one({"_id": resultado.inserted_id})
    return jsonify(convertir_a_json(guardado)), 201


# Consultar presupuesto de un usuario
@app.route("/presupuesto/<user_id>", methods=["GET"])
def ver_presupuesto(user_id):
    presupuesto = coleccion_presupuestos.find_one({"user_id": user_id})
    if not presupuesto:
        return jsonify({"mensaje": "No existe presupuesto para este usuario"}), 404
    return jsonify(convertir_a_json(presupuesto))


# Actualizar presupuesto de un usuario
@app.route("/presupuesto/<user_id>", methods=["PUT"])
def actualizar_presupuesto(user_id):
    datos = request.get_json() or {}
    cambios = {}

    if "ingreso_mensual" in datos:
        try:
            cambios["ingreso_mensual"] = float(datos["ingreso_mensual"])
        except:
            return jsonify({"mensaje": "ingreso_mensual debe ser numérico"}), 400

    if "gasto_maximo" in datos:
        try:
            cambios["gasto_maximo"] = float(datos["gasto_maximo"])
        except:
            return jsonify({"mensaje": "gasto_maximo debe ser numérico"}), 400

    if not cambios:
        return jsonify({"mensaje": "No hay campos para actualizar"}), 400

    resultado = coleccion_presupuestos.update_one({"user_id": user_id}, {"$set": cambios})
    if resultado.matched_count == 0:
        return jsonify({"mensaje": "No existe presupuesto para este usuario"}), 404

    actualizado = coleccion_presupuestos.find_one({"user_id": user_id})
    return jsonify(convertir_a_json(actualizado))


if __name__ == "__main__":
    app.run(debug=True, port=5002)
