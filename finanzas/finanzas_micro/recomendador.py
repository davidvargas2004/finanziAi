import os
import json
from datetime import datetime
from dotenv import load_dotenv
import cohere
from pymongo import MongoClient

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["finanzas_db"]
mongo_collection = mongo_db["registros"]

# Configuración de Cohere
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.Client(COHERE_API_KEY)

# Generación de recomendaciones usando Cohere (chat)
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
        response = co.chat(
            model="command-r",
            message=prompt,
            temperature=0.7
        )
        return response.text.strip()
    except Exception as e:
        print("Error al generar recomendación:", e)
        return "Recomendación no disponible temporalmente"

# Guardar datos en MongoDB
def guardar_en_mongo(data):
    try:
        mongo_collection.insert_one(data)
        print("Datos guardados en MongoDB correctamente.")
    except Exception as e:
        print("Error al guardar en MongoDB:", e)

# Guardar datos en archivo JSON local
def guardar_json(data):
    try:
        DATA_DIR = "financial_data"
        os.makedirs(DATA_DIR, exist_ok=True)
        filename = f"{DATA_DIR}/{data.get('usuario_id', 'anonimo')}_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Datos guardados en {filename}")
    except Exception as e:
        print("Error al guardar JSON:", e)
