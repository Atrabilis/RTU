import re
import pandas as pd

ASDU_TYPES_CSV = 'ASDU_types.csv'

def analizar_iec104(mensaje):
    # Leer el archivo CSV
    asdu_types_df = pd.read_csv(ASDU_TYPES_CSV)

    # Verificar la longitud del mensaje
    if len(mensaje) < 4:
        return "Mensaje demasiado corto"

    # Extraer el campo de inicio y de longitud
    start_field = mensaje[0]
    length_field = mensaje[1]

    # Verificar el campo de inicio
    if start_field != 0x68:
        return "Campo de inicio inválido"

    # Extraer el campo de control (CF)
    control_field = mensaje[2:6]  # Corrección aquí

    # Determinar el formato de la APDU
    cf1 = control_field[0]
    apdu_format = "I" if cf1 & 0x03 == 0 else "S" if cf1 & 0x03 == 1 else "U"
    u_type = None
    type_id = None

    if apdu_format == "U":
        # Determinar el tipo de mensaje U
        if cf1 == 0x43:
            u_type = "Test Frame Activation"
        elif cf1 == 0x83:
            u_type = "Test Frame Confirmation"
        elif cf1 == 0x13:
            u_type = "Stop Data Transfer Activation"
        elif cf1 == 0x23:
            u_type = "Stop Data Transfer Confirmation"
        elif cf1 == 0x07:
            u_type = "Start Data Transfer Activation"
        elif cf1 == 0x0B:
            u_type = "Start Data Transfer Confirmation"

    # Extraer el campo de datos (ASDU)
    asdu = mensaje[6:]  # Corrección aquí

    if apdu_format == "I":
        # Extraer el Type Identification para formato I
        type_id = asdu[0]
        
        # Buscar la Description y la Reference en el DataFrame
        type_info = asdu_types_df[asdu_types_df['Type'] == type_id]
        if not type_info.empty:
            description = type_info['Description'].values[0]
            print(description)
            reference = type_info['Reference'].values[0]
        else:
            description = reference = "Unknown"
    else:
        description = reference = None

    return {
        "start_field": start_field,
        "length_field": length_field,
        "control_field": control_field,
        "apdu_format": apdu_format,
        "u_type": u_type,
        "asdu": {
            "type_id": type_id,
            "description": description,
            "reference": reference,
            "data": asdu[1:]  # Datos restantes de la ASDU
        }
    }


def analizar_archivo(nombre_archivo):
    # Leer el archivo línea por línea
    with open(nombre_archivo, 'r') as archivo:
        lineas = archivo.readlines()

    # Iterar sobre cada línea y extraer la secuencia de bytes
    secuencias_bytes = []
    for linea in lineas:
        # Buscar la posición de -> o <- en la línea
        pos = linea.find('->')
        if pos == -1:
            pos = linea.find('<-')
        if pos != -1:
            # Extraer la secuencia de bytes de la línea
            bytes_hex = linea[pos+2:].strip()
            secuencias_bytes.append(bytes_hex)

    # Iterar sobre cada secuencia de bytes y analizar
    resultados = []
    for bytes_hex in secuencias_bytes:
        # Convertir la secuencia de bytes a un objeto bytes real
        bytes_real = bytes.fromhex(bytes_hex)
        # Analizar la secuencia de bytes con la función analizar_iec104
        resultado = analizar_iec104(bytes_real)
        # Almacenar el resultado
        resultados.append(resultado)

    # Mostrando los resultados
    for res in resultados:
        print(res)

# Llamar a la función analizar_archivo
analizar_archivo('traffic_test.txt')
