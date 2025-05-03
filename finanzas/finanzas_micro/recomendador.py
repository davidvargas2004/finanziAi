import os
import json
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["finanzas_db"]
mongo_collection = mongo_db["registros"]

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-pro")

def generate_gemini_recommendation(financial_data: dict) -> str:
    prompt = f"""
Eres un asesor financiero profesional. Analiza los siguientes datos financieros en pesos colombianos:

- Ingresos mensuales: {financial_data['ingresos_mensuales']}
- Gastos mensuales: {financial_data['gastos_mensuales']}
- Meta de ahorro: {financial_data['metas_financieras'].get('ahorro', 0)}
- Ahorro mensual actual: {financial_data['ahorro_mensual']}

Genera exactamente 3 recomendaciones claras y numeradas, cada una en una línea separada, con este formato:

1. ...
2. ...
3. ...
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response and response.text else "Recomendación no disponible temporalmente"
    except Exception as e:
        return "Recomendación no disponible temporalmente"
    
def guardar_en_mongo(data):
    mongo_collection.insert_one(data)

def guardar_json(data):
    DATA_DIR = "financial_data"
    os.makedirs(DATA_DIR, exist_ok=True)
    filename = f"{DATA_DIR}/{data.get('usuario_id', 'anonimo')}_{datetime.now().strftime('%Y%m%d')}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
