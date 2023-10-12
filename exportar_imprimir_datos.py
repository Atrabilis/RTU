import json
from bson import ObjectId, Binary
from pymongo import MongoClient
from funciones import *

def export_data():
    mongoclient = MongoClient('localhost', 27017)
    db = mongoclient.datosRTU
    collection = db.datos
    
    cursor = collection.find({})

    # Convertir los documentos a una lista de diccionarios
    data = list(cursor)

    # Convertir ObjectId y datos binarios para hacerlos serializables
    def handle_encoding(obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, bytes):
            return obj.decode('utf-8', 'ignore')  # o usa obj.hex() para una representación hexadecimal
        raise TypeError(f"Object of type '{type(obj).__name__}' is not JSON serializable")

    # Convertir los datos a una cadena JSON
    json_data = json.dumps(data, default=handle_encoding)

    # Escribir la cadena JSON a un archivo
    with open('data_export.json', 'w') as f:
        f.write(json_data)

    # Imprimir los datos
    for document in data:
        imprimir_resultados(document)

if __name__ == "__main__":
    try:
        export_data()
        print("Data exported successfully.")
    except Exception as e:
        print(f"An error occurred while exporting data: {str(e)}")
