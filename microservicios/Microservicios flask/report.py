from flask import Flask, jsonify, send_file
import requests, io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# URLs de los otros microservicios
PRESUPUESTOS_URL = "http://localhost:5001"
TRANSACCIONES_URL = "http://localhost:5000"

@app.route("/")
def indice():
    return "ON FUNCIONANDO"


#Gera PDF
@app.route("/reportes/<user_id>/<mes>/pdf", methods=["GET"])
def reporte_pdf(user_id, mes):
 #Pedimos informacion de presupuesto y transacciones
    r_p = requests.get(f"{PRESUPUESTOS_URL}/presupuesto/{user_id}")
    r_t = requests.get(f"{TRANSACCIONES_URL}/transacciones/resumen/{user_id}/{mes}")

    if r_p.status_code != 200 or r_t.status_code != 200:
        return jsonify({"mensaje": "Error consultando servicios"}), 502

    ppto = r_p.json()
    resumen = r_t.json()

    ingreso = ppto.get("ingreso", 0)
    limite = ppto.get("gasto", 0)
    gastos = resumen.get("total_gastos", 0)

#Creacion del PDF
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



#Genracion del Excel
@app.route("/reportes/<user_id>/<mes>/excel", methods=["GET"])
def reporte_excel(user_id, mes):
    r_p = requests.get(f"{PRESUPUESTOS_URL}/presupuesto/{user_id}")
    r_t = requests.get(f"{TRANSACCIONES_URL}/transacciones/resumen/{user_id}/{mes}")

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
