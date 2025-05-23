# finanzas_micro/recomendador.py

import os
import json
from datetime import datetime
from dotenv import load_dotenv # Asegúrate de que esto esté aquí
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import cohere

# --- Punto A: Inmediatamente después de cargar dotenv ---
load_dotenv()
print(f"[DEBUG A] MONGO_URI leída por dotenv: {os.getenv('MONGO_URI')}")

_mongo_client = None
_mongo_db = None
_mongo_collection = None

def get_mongo_collection():
    global _mongo_client, _mongo_db, _mongo_collection

    if _mongo_collection is not None:
        return _mongo_collection

    MONGO_URI_FROM_GETENV = os.getenv("MONGO_URI")
    # --- Punto B: Dentro de get_mongo_collection() antes de la conexión ---
    print(f"[DEBUG B] MONGO_URI usada para la conexión: {MONGO_URI_FROM_GETENV}")

    if not MONGO_URI_FROM_GETENV:
        print("ERROR: La variable de entorno MONGO_URI no está configurada. No se puede conectar a MongoDB Atlas.")
        return None

    try:
        _mongo_client = MongoClient(MONGO_URI_FROM_GETENV)
        _mongo_client.admin.command('ping')
        print("Conexión a MongoDB Atlas establecida con éxito!")

        _mongo_db = _mongo_client["finanzas_db"]
        _mongo_collection = _mongo_db["registros"]

        return _mongo_collection

    except ConnectionFailure as e:
        print(f"ERROR DE CONEXIÓN A MONGODB ATLAS: No se pudo conectar. Verifica tu MONGO_URI, IP y credenciales en Atlas. Detalles: {e}")
        _mongo_client = None
        _mongo_db = None
        _mongo_collection = None
        return None
    except Exception as e:
        print(f"ERROR INESPERADO AL INTENTAR CONECTAR A MONGODB ATLAS: {e}")
        _mongo_client = None
        _mongo_db = None
        _mongo_collection = None
        return None

_cohere_client = None
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

if not COHERE_API_KEY:
    print("ADVERTENCIA: La variable de entorno COHERE_API_KEY no está configurada. Las recomendaciones de IA no funcionarán.")
else:
    try:
        _cohere_client = cohere.Client(COHERE_API_KEY)
        print("Cliente Cohere inicializado.")
    except Exception as e:
        print(f"ERROR: No se pudo inicializar el cliente Cohere. Las recomendaciones de IA no funcionarán. Detalles: {e}")
        _cohere_client = None

def generate_cohere_recommendation(financial_data: dict) -> str:
    if _cohere_client is None:
        return "Recomendación no disponible: El cliente de Cohere no se pudo inicializar."

    prompt = f"""
Eres un asesor financiero profesional. Analiza los siguientes datos financieros en pesos colombianos, toma en cuenta la vida económica de un colombiano promedio
y ten en cuenta que el ingreso mensual es el 100% para los cálculos de porcentaje de gastos:

- Ingresos mensuales: {financial_data['ingresos_mensuales']}
- Gastos de Alimentación: {financial_data['gastos_mensuales'].get('Alimentación', 0)}
- Gastos de Transporte: {financial_data['gastos_mensuales'].get('Transporte', 0)}
- Gastos de Entretenimiento: {financial_data['gastos_mensuales'].get('Entretenimiento', 0)}
- Gastos de Hogar: {financial_data['gastos_mensuales'].get('Hogar', 0)}
- Total de Gastos Mensuales: {sum(financial_data['gastos_mensuales'].values())}
- Meta de ahorro: {financial_data['metas_financieras'].get('ahorro', 0)}
- Ahorro mensual actual: {financial_data['ahorro_mensual']}

Genera exactamente 3 recomendaciones no tan cortas, claras y numeradas, cada una en una línea separada, con este formato:

1. ...
2. ...
3. ...
    """
    try:
        print("\n--- Enviando prompt a Cohere ---")
        response = _cohere_client.generate(
            model='command-r-plus',
            prompt=prompt,
            max_tokens=250,
            temperature=0.7,
            num_generations=1
        )
        print("--- Respuesta del modelo Cohere recibida ---")
        if response and response.generations:
            return response.generations[0].text.strip()
        else:
            return "Recomendación no disponible temporalmente (respuesta vacía o inválida de Cohere)."
    except Exception as e:
        print(f"Error al generar recomendación con Cohere: {e}")
        return f"Recomendación no disponible temporalmente (Error de Cohere: {e})"

def guardar_en_mongo(data):
    collection = get_mongo_collection()
    if collection is not None:
        try:
            # --- MODIFICACIÓN TEMPORAL PARA DEBUGGING (QUITAR LUEGO) ---
            # Esto asegura un _id único para cada inserción de prueba
            from bson.objectid import ObjectId
            if '_id' in data and isinstance(data['_id'], str) and len(data['_id']) == 24: # Asumiendo que es un ObjectId en string
                # Si ya tiene un _id y es un string (como si viniera de JSON), forzamos uno nuevo para la prueba
                # O si sospechas que el ID '682ff76da491168f16722cf2' se está reusando:
                print(f"[DEBUG] Se detectó _id existente: {data['_id']}. Forzando nuevo ObjectId para depuración.")
                data['_id'] = ObjectId()
            elif '_id' not in data:
                data['_id'] = ObjectId()
            # --- FIN MODIFICACIÓN TEMPORAL ---

            result = collection.insert_one(data)
            print(f"Documento insertado en MongoDB Atlas con ID: {result.inserted_id}")
            return True
        except OperationFailure as e:
            if e.code == 11000: # Duplicate Key Error
                print(f"ERROR: Documento con _id {data.get('_id')} ya existe. Intenta con un nuevo ID o maneja el duplicado.")
            else:
                print(f"ERROR al insertar documento en MongoDB (OperationFailure). Detalles: {e.details}")
            return False
        except Exception as e:
            print(f"ERROR inesperado al insertar documento en MongoDB: {e}")
            return False
    else:
        print("ADVERTENCIA: No se pudo obtener la colección de MongoDB para guardar el documento. (Conexión fallida previamente)")
        return False

def guardar_json(data):
    DATA_DIR = "financial_data"
    os.makedirs(DATA_DIR, exist_ok=True)
    filename = f"{DATA_DIR}/{data.get('usuario_id', 'anonimo')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Datos guardados en JSON local: {filename}")

if __name__ == "__main__":
    print("\n--- Iniciando prueba de finanzas_micro/recomendador.py ---")

    load_dotenv() # Asegúrate de cargar .env para la prueba directa también

    # --- Punto C: En el bloque __main__ para depuración ---
    print(f"[DEBUG C] MONGO_URI en __main__: {os.getenv('MONGO_URI')}")

    datos_financieros_ejemplo_test = {
        "ingresos_mensuales": 3000000,
        "gastos_mensuales": {
            "Alimentación": 800000,
            "Transporte": 400000,
            "Entretenimiento": 300000,
            "Hogar": 500000
        },
        "metas_financieras": {"ahorro": 4000000},
        "ahorro_mensual": 1000000,
        "usuario_id": "test_usuario_direct_run_" + datetime.now().strftime('%Y%m%d%H%M%S')
    }

    print("\n>>> Probando generate_cohere_recommendation...")
    recomendacion_test = generate_cohere_recommendation(datos_financieros_ejemplo_test)
    print("\n--- Recomendación de Cohere (Resultado de prueba) ---")
    print(recomendacion_test)

    print("\n>>> Probando guardar_en_mongo...")
    guardado_exitoso_test = guardar_en_mongo(datos_financieros_ejemplo_test)
    if guardado_exitoso_test:
        print("¡Documento de prueba enviado a MongoDB Atlas con éxito!")
    else:
        print("Fallo al guardar documento de prueba en MongoDB Atlas. Revisa los errores anteriores.")

    print("\n>>> Probando guardar_json...")
    guardar_json(datos_financieros_ejemplo_test)
    print("--- Prueba de finanzas_micro/recomendador.py finalizada ---")