from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

API_KEY = "OnceCaldasQuerido"

# Verificamos API KEY de quien llama a notificaciones (gateway)
@app.before_request
def verificar():
    api_key = request.headers.get('X-API-KEY')
    if api_key != API_KEY:
        return jsonify({"error": "No tienes permiso"}), 401

# Endpoints de microservicios a conectar (directo, no por gateway)
presupuestos_url = "http://localhost:5001"
transacciones_url = "http://localhost:5000"

alerta = 0.8

@app.route("/")
def indice():
    return "ON FUNCIONANDO"

# Consulta de estado de un usuario
@app.route("/notificaciones/<user_id>/<mes>", methods=["GET"])
def noti_user(user_id, mes):
    # Headers internos para llamar a otros microservicios
    headers = {"X-API-KEY": API_KEY}

    # 1) Revisamos el presupuesto del usuario
    respuesta_p = requests.get(
        f"{presupuestos_url}/presupuesto/{user_id}",
        headers=headers
    )
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

    # 2) Revisamos el total de gastos del mes
    respuesta_t = requests.get(
        f"{transacciones_url}/transacciones/resumen/{user_id}/{mes}",
        headers=headers
    )
    if respuesta_t.status_code != 200:
        return jsonify({"mensaje": "Error al encontrar el resultado"}), 502

    resumen = respuesta_t.json()
    # OJO: aqui el microservicio de transacciones devuelve "total_gastos"
    totalg = float(resumen.get("total_gastos", 0))

    # 3) Realizamos la comparación de gastos con límite
    ratio = totalg / limite if limite > 0 else 0

    if totalg > limite:
        estado = "EXCEDIDO"
        mensaje = f"Te pasaste del limite: {totalg:.2f} / {limite:.2f}"
    elif ratio >= alerta:
        estado = "ALERTA"
        mensaje = f"Ya llevas el {ratio*100:.0f}% de tu límite: {totalg:.2f} / {limite:.2f}"
    else:
        estado = "OK"
        mensaje = f"Estas bien pero no te relajes: {totalg:.2f} / {limite:.2f}"

    # Respuesta del endpoint
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
