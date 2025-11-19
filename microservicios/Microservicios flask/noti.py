from flask import Flask, jsonify, requests


app = Flask(__name__)


API_KEY = "OnceCaldasQuerido"

#Verificamos que la request que recibimos sea realizada con el header de la API key que tenemos, para validar qu solo la api key obtenga una respuesta

def verificar():
    api_key = request.headers.get('X-API-KEY')
    if api_key != API_KEY:
        return jsonify({"error": "No tienes permiso"}), 401

#Endpoints de microservicios a conectar
presupuestos_url = "http://localhost:5001"
transacciones_url = "http://localhost:5000"


alerta = 0.8


@app.route("/")
def indice():
    return "ON FUNCIONANDO"


#Consulta de estado de un usuario
@app.route("/notificaciones/<user_id>/<mes>", methods=["GET"])
def noti_user(user_id, mes):

#Revisamos el presupuesto del usuario
    respuesta_p = requests.get(f"{presupuestos_url}/presupuesto/{user_id}")
    if respuesta_p.status_code != 200:
        return jsonify({"mensaje": "Error al encontrar el resultado"}), 502

    presupuesto = respuesta_p.json()
    limite = float(presupuesto.get("gasto", 0))

    if limite <= 0:
        return jsonify({
            "user_id": user_id,
            "mes": mes,
            "estado": "No Limite",
            "mensaje": "No esta configurado el limite"
        })

#Revisamos el total de gastos del mes 
    respuesta_t = requests.get(f"{transacciones_url}/transacciones/resumen/{user_id}/{mes}")
    if respuesta_t.status_code != 200:
        return jsonify({"mensaje": "Error al encontrar el resultado"}), 502

    resumen = respuesta_t.json()
    totalg = float(resumen.get("totalg", 0))

#Realizamos la comparacion de gastos con limites para determinar 
    ratio = totalg / limite
    if totalg > limite:
        estado = "EXCEDIDO"
        mensaje = f"Te pasaste del limite: {totalg:.2f} / {limite:.2f}"
    elif ratio >= alerta:
        estado = "ALERTA"
        mensaje = f"Ya llevas el {ratio*100:.0f}% de tu límite: {totalg:.2f} / {limite:.2f}"
    else:
        estado = "OK"
        mensaje = f"Estas bien pero no te relajes: {totalg:.2f} / {limite:.2f}"

#Respuesta del endpoint
    return jsonify({
        "user_id": user_id,
        "mes": mes,
        "total_gastos": totalg,
        "limite": limite,
        "estado": estado,
        "mensaje": mensaje
    })


if __name__ == "__main__":
    app.run(debug=True, port=5003)