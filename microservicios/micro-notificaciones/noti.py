from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)

API_KEY = "OnceCaldasQuerido"

# Verificamos API KEY de quien llama a notificaciones (gateway)
@app.before_request
def verificar():
    api_key = request.headers.get('X-API-KEY')
    if api_key != API_KEY:
        return jsonify({"error": "No tienes permiso"}), 401

# Endpoints de microservicios a conectar (directo, no por gateway)
presupuestos_url = os.getenv("PRESUPUESTOS_URL", "http://micro-presupuestos:5001")
transacciones_url = os.getenv("TRANSACCIONES_URL", "http://micro-transacciones:5000")

# ALERTA tomada desde el .env o fallback a 0.8
alerta = float(os.getenv("ALERTA", 0.8))

@app.route("/")
def indice():
    return "ON FUNCIONANDO"

# Consulta de estado de un usuario
@app.route("/notificaciones/<user_id>/<mes>", methods=["GET"])
def noti_user(user_id, mes):
    headers = {"X-API-KEY": API_KEY}

    # 1) Revisamos el presupuesto del usuario
    try:
        respuesta_p = requests.get(
            f"{presupuestos_url}/presupuesto/{user_id}",
            headers=headers,
            timeout=3
        )
    except Exception:
        return jsonify({"mensaje": "Error conectando a micro-presupuestos"}), 502

    if respuesta_p.status_code != 200:
        return jsonify({"mensaje": "Error al encontrar el resultado"}), 502

    presupuesto = respuesta_p.json()
    limite = float(presupuesto.get("gasto", 0))

    if limite <= 0:
        return jsonify({
            "user_id": user_id,
            "mes": mes,
            "estado": "No Limite",
            "mensaje": "No está configurado el límite"
        })

    # 2) Revisamos el total de gastos del mes
    try:
        respuesta_t = requests.get(
            f"{transacciones_url}/transacciones/resumen/{user_id}/{mes}",
            headers=headers,
            timeout=3
        )
    except Exception:
        return jsonify({"mensaje": "Error conectando a micro-transacciones"}), 502

    if respuesta_t.status_code != 200:
        return jsonify({"mensaje": "Error al encontrar el resultado"}), 502

    resumen = respuesta_t.json()
    totalg = float(resumen.get("total_gastos", 0))

    # 3) Comparación
    ratio = totalg / limite if limite > 0 else 0

    if totalg > limite:
        estado = "EXCEDIDO"
        mensaje = f"Te pasaste del límite: {totalg:.2f} / {limite:.2f}"
    elif ratio >= alerta:
        estado = "ALERTA"
        mensaje = f"Ya llevas el {ratio*100:.0f}% de tu límite: {totalg:.2f} / {limite:.2f}"
    else:
        estado = "OK"
        mensaje = f"Estás bien pero pilas: {totalg:.2f} / {limite:.2f}"

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
