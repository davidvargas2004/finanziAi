import os
import json
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
import google.generativeai as genai

# Cargar variables de entorno (.env debe tener MONGO_URI y GEMINI_API_KEY)
load_dotenv()

# === CONFIGURACIÓN MONGO ATLAS ===
MONGO_URI = os.getenv("MONGO_URI")
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["finanzas_db"]
mongo_collection = mongo_db["registros"]

# === CONFIGURACIÓN GEMINI ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-pro")  # Puedes cambiar a "gemini-pro" si ese es tu modelo habilitado

# === GENERAR RECOMENDACIONES CON GEMINI ===
def generate_gemini_recommendation(financial_data: dict) -> str:
    prompt = f"""
Eres un asesor financiero profesional. Analiza los siguientes datos financieros en pesos colombianos:

- Ingresos mensuales: {financial_data['ingresos_mensuales']}
- Gastos mensuales: {financial_data['gastos_mensuales']}
- Meta de ahorro: {financial_data['metas_financieras'].get('ahorro', 0)}
- Ahorro mensual actual: {financial_data['ahorro_mensual']}

Genera exactamente 3 recomendaciones claras, útiles y numeradas, cada una en una línea separada, con este formato:

1. ...
2. ...
3. ...
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response and response.text else "Recomendación no disponible temporalmente"
    except Exception as e:
        print("Error al generar recomendación:", e)
        return "Recomendación no disponible temporalmente"

# === GUARDAR EN MONGODB ATLAS ===
def guardar_en_mongo(data):
    try:
        mongo_collection.insert_one(data)
        print("✅ Datos guardados en MongoDB Atlas.")
    except Exception as e:
        print("❌ Error al guardar en MongoDB:", e)

# === OPCIONAL: GUARDAR EN JSON LOCAL ===
def guardar_json(data):
    try:
        DATA_DIR = "financial_data"
        os.makedirs(DATA_DIR, exist_ok=True)
        filename = f"{DATA_DIR}/{data.get('usuario_id', 'anonimo')}_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"📝 Datos guardados en {filename}")
    except Exception as e:
        print("❌ Error al guardar JSON:", e)
