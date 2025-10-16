from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

#Conexion a Mongo
cliente_mongo = MongoClient("mongodb://localhost:27017/")
base_datos = cliente_mongo["ppto"]
coleccion = base_datos["presupuestos"]

#Compatibilidad con mongo
def convertir_a_json(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


@app.route("/")
def indice():
    return "ON FUNCIONANDO"


#Ingresar un presupuesto a un usuario
@app.route("/presupuesto", methods=["POST"])
def crear_ppto():
    datos = request.get_json()

#validamos que la peticion tenga datos
    if not datos:
        return jsonify({"mensaje": "No hay datos"}), 400
    
#Validamos que los campos ingreso mensual y gasto maximo existan 

    if "user_id" not in datos or "ingreso" not in datos or "gasto" not in datos:
        return jsonify({"mensaje": "Ingresa todos los datos correspondientes"}), 400

 #Validamos que ese usuario no tenga un presupuesto ya asignado
 
    if coleccion.find_one({"user_id": datos["user_id"]}):
        return jsonify({"mensaje": "Usuario ya tiene presupuesto"}), 400

#Validamos que el ingreso y gasto sean numeros

    try:
        ingreso = float(datos["ingreso"])
        gasto = float(datos["gasto"])
    except:
        return jsonify({"mensaje": "No son numeros"}), 400

#Guardamos en la base de datos

    documento = {
        "user_id": datos["user_id"],
        "ingreso": ingreso,
        "gasto": gasto
    }

    resultado = coleccion.insert_one(documento)
    guardado = coleccion.find_one({"_id": resultado.inserted_id})
    return jsonify(convertir_a_json(guardado)), 201


#Consultamos cual es el presupuesto de un suaurio
@app.route("/presupuesto/<user_id>", methods=["GET"])
def ver_ppto(user_id):
    presupuesto = coleccion.find_one({"user_id": user_id})
    if not presupuesto:
        return jsonify({"mensaje": "No tiene presupuesto"}), 404
    return jsonify(convertir_a_json(presupuesto))

# Actualizar presupuesto de un usuario
@app.route("/presupuesto/<user_id>", methods=["PUT"])
def actualizar_presupuesto(user_id):
    datos = request.get_json()

#Si no hay datos al recibir
    if not datos:
        return jsonify({"mensaje": "No hay datos"}), 400

    cambios = {}


#Si el ingreso no es un numero
    if "ingreso" in datos:
        try:
            cambios["ingreso"] = float(datos["ingreso"])
        except:
            return jsonify({"mensaje": "El ingreso mensual debe ser un numero"}), 400

#Si el gasto no es un numero
    if "gasto" in datos:
        try:
            cambios["gasto"] = float(datos["gasto"])
        except:
            return jsonify({"mensaje": "gasto debe ser un numero"}), 400

#Si no se realizaron cambios 
    if not cambios:
        return jsonify({"mensaje": "No hay nada que actualizar"}), 400

    #Realizamos la actualizacion
    resultado = coleccion.update_one({"user_id": user_id}, {"$set": cambios})
    if resultado.matched_count == 0:
        return jsonify({"mensaje": "No hay presupuesto para ese usuario"}), 404

    actualizado = coleccion.find_one({"user_id": user_id})
    return jsonify(convertir_a_json(actualizado))



if __name__ == "__main__":
    app.run(debug=True, port=5001)
