from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

#Conexion a Mongo
cliente_mongo = MongoClient("mongodb://localhost:27017/")
base_datos = cliente_mongo["tx"]
coleccion = base_datos["transacciones"]

#Compatibilidad con mongo
def convertir_a_json(doc):
    """Convierte el _id de Mongo a string y lo renombra a 'id'."""
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


@app.route("/")
def indice():
    return "ON FUNCIONANDO"

#Creamos una tx con lo datos tipo,monto y fecha.

@app.route("/transacciones", methods=["POST"])
def crear_tx():
    datos = request.get_json()


#validamos que la peticion tenga datos
    if not datos:
        return jsonify({"mensaje": "Sin datos"}), 400

    tipo = datos.get("tipo")
    monto = datos.get("monto")
    fecha = datos.get("fecha")
    
#Validamos que los campos tipo, monto y fechas existan

    if not tipo or not monto or not fecha:
        return jsonify({"mensaje": "Todos los campos son obligatorios"}), 400
    
 #Validamos que venga el user id    
    if not datos.get("user_id"):
        return jsonify({"mensaje": "Falta user_id"}), 400

#Validamos que el tipo de tx sea de ingreso o gasto
    if tipo not in ("gasto", "ingreso"):
        return jsonify({"mensaje": "Especifica si es gasto o ingreso'"}), 400

#convertimos el monto en float y si falla es por que no es un numero
    try:
        monto = float(monto)
    except:
        return jsonify({"mensaje": "El monto debe ser un numero"}), 400

#Creamos el documento con los datos a guardar 
    documento = {
        "user_id": datos.get("user_id"),
        "tipo": tipo,
        "monto": monto,
        "fecha": fecha,  
        "categoria_id": datos.get("categoria_id"),
        "descripcion": datos.get("descripcion", "")
    }

#Guardamos el documento y modificamos el id para que se pueda enviar en formato JSON
    resultado = coleccion.insert_one(documento)
    guardado = coleccion.find_one({"_id": resultado.inserted_id})
#Retornamos la respuesta 
    return jsonify(convertir_a_json(guardado)), 201


#Metodo para ver las transacciones 
@app.route("/transacciones/<user_id>", methods=["GET"])
def ver_tx(user_id):
    cursor = coleccion.find({"user_id": user_id}).sort("fecha", -1)
    return jsonify([convertir_a_json(x) for x in cursor])


#Metodo para actualizar una transaccion
@app.route("/transacciones/<transaccion_id>", methods=["PUT"])
def actualizar_tx(transaccion_id):
    
#Consultamos que el id exista en nuestra base de datos
    try:
        _id = ObjectId(transaccion_id)
    except Exception:
        return jsonify({"mensaje": "id no valido"}), 400

    datos = request.get_json() or {}
    cambios = {}

#Validamos que el tipo de transaccion sea gasto o ingreso
    if "tipo" in datos:
        if datos["tipo"] not in ("gasto", "ingreso"):
            return jsonify({"mensaje": "Debe ser gasto o ingreso'"}), 400
        cambios["tipo"] = datos["tipo"]

#Validamos que el monto sea un numero y que no sea menor que 0
    if "monto" in datos:
        try:
            monto = float(datos["monto"])
        except Exception:
            return jsonify({"mensaje": "Monto debe ser un numero"}), 400
        if monto <= 0:
            return jsonify({"mensaje": "El monto no debe ser menos que 0"}), 400
        cambios["monto"] = monto

#Si el cambio es fecha categoria o descripcion realizamos los cambios 
    if "fecha" in datos:
        cambios["fecha"] = datos["fecha"]

    if "categoria_id" in datos:
        cambios["categoria_id"] = datos["categoria_id"]

    if "descripcion" in datos:
        cambios["descripcion"] = datos["descripcion"]
#Validamos que si no hay cambios retornar que no se hicieron cambios
    if not cambios:
        return jsonify({"mensaje": "Debes actualizar "}), 400
#Guardamos al realizar los cam bios
    resultado = coleccion.update_one({"_id": _id}, {"$set": cambios})
    if resultado.matched_count == 0:
        return jsonify({"mensaje": "Transacción no encontrada"}), 404
#Retornamos tipo JSON
    guardado = coleccion.find_one({"_id": _id})
    return jsonify(convertir_a_json(guardado))


#Eliminar una transaccion

@app.route("/transacciones/<transaccion_id>", methods=["DELETE"])
def eliminar_transaccion(transaccion_id):
    
#Consultamos que el id exista en nuestra base de datos si no lo encuentra es un id no valido
    try:
        _id = ObjectId(transaccion_id)
    except Exception:
        return jsonify({"mensaje": "id no valido"}), 400

    resultado = coleccion.delete_one({"_id": _id})
    if resultado.deleted_count == 0:
        return jsonify({"mensaje": "Tx no existe"}), 404

    return jsonify({"eliminado": True, "id": transaccion_id})


#Resumen general de los gastos mensuales de esa id 
@app.route("/transacciones/resumen/<user_id>/<mes>", methods=["GET"])
def resumen_mensual(user_id, mes):
    if not mes or len(mes) != 7 or mes[4] != "-":
        return jsonify({"mensaje": "mes debe ser 'YYYY-MM'"}), 400

    prefijo = mes + "-"
    cursor = coleccion.find({
        "user_id": user_id,
        "fecha": {"$regex": f"^{prefijo}"},
        "tipo": "gasto"
    })

    total_gastos = sum(float(doc.get("monto", 0)) for doc in cursor)

    return jsonify({
        "mes": mes,
        "user_id": user_id,
        "total_gastos": total_gastos
    })
if __name__ == "__main__":
    app.run(debug=True, port=5000)
