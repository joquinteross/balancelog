from flask import Flask, jsonify, send_file, request
import requests, io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

API_KEY = "OnceCaldasQuerido"


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200




@app.before_request
def verificar():
    api_key = request.headers.get('X-API-KEY')
    if api_key != API_KEY:
        return jsonify({"error": "No tienes permiso"}), 401

# URLs de los otros microservicios
presupuestos_url = os.getenv("PRESUPUESTOS_URL", "http://micro-presupuestos:5001")
transacciones_url = os.getenv("TRANSACCIONES_URL", "http://micro-transacciones:5000")

@app.route("/")
def indice():
    return "ON FUNCIONANDO"

@app.route("/reportes/<user_id>/<mes>/pdf", methods=["GET"])
def reporte_pdf(user_id, mes):

    headers = {"X-API-KEY": API_KEY}

    r_p = requests.get(f"{presupuestos_url}/presupuesto/{user_id}", headers=headers)
    r_t = requests.get(f"{transacciones_url}/transacciones/resumen/{user_id}/{mes}", headers=headers)

    if r_p.status_code != 200 or r_t.status_code != 200:
        return jsonify({"mensaje": "Error consultando servicios"}), 502

    ppto = r_p.json()
    resumen = r_t.json()

    ingreso = ppto.get("ingreso", 0)
    limite = ppto.get("gasto", 0)
    gastos = resumen.get("total_gastos", 0)

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "Reporte Mensual - Finanzas")

    c.setFont("Helvetica", 12)
    c.drawString(50, 700, f"Usuario: {user_id}")
    c.drawString(50, 680, f"Mes: {mes}")
    c.drawString(50, 660, f"Ingreso mensual: {ingreso}")
    c.drawString(50, 640, f"Límite de gasto: {limite}")
    c.drawString(50, 620, f"Gastos del mes: {gastos}")

    c.drawString(50, 590, f"Generado en: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.showPage()
    c.save()

    buffer.seek(0)
    return send_file(buffer, as_attachment=True,
                     download_name=f"reporte_{user_id}_{mes}.pdf",
                     mimetype="application/pdf")

@app.route("/reportes/<user_id>/<mes>/excel", methods=["GET"])
def reporte_excel(user_id, mes):

    headers = {"X-API-KEY": API_KEY}

    r_p = requests.get(f"{presupuestos_url}/presupuesto/{user_id}", headers=headers)
    r_t = requests.get(f"{transacciones_url}/transacciones/resumen/{user_id}/{mes}", headers=headers)

    if r_p.status_code != 200 or r_t.status_code != 200:
        return jsonify({"mensaje": "Error consultando servicios"}), 502

    ppto = r_p.json()
    resumen = r_t.json()

    ingreso = ppto.get("ingreso", 0)
    limite = ppto.get("gasto", 0)
    gastos = resumen.get("total_gastos", 0)

    datos = [{
        "Usuario": user_id,
        "Mes": mes,
        "Ingreso mensual": ingreso,
        "Límite de gasto": limite,
        "Gastos del mes": gastos
    }]
    
    df = pd.DataFrame(datos)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Resumen")

    output.seek(0)
    return send_file(output, as_attachment=True,
                     download_name=f"reporte_{user_id}_{mes}.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    app.run(debug=True, port=5004)
