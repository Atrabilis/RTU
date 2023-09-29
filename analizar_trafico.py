import pandas as pd

ASDU_TYPES_CSV = 'ASDU_types.csv'

def analizar_iec104(mensaje, direccion):
    asdu_types_df = pd.read_csv(ASDU_TYPES_CSV)

    if len(mensaje) < 4:
        return {"error": "Mensaje demasiado corto", "direccion": direccion}

    start_field = mensaje[0]

    if start_field != 0x68:
        return {"error": "Campo de inicio inválido", "direccion": direccion}

    control_field = mensaje[2:6]

    cf1 = control_field[0]
    apdu_format = "I" if (cf1 & 0x01) == 0 else "S" if (cf1 & 0x03) == 1 else "U"
    u_type = None
    type_id = None

    if apdu_format == "U":
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

    asdu = mensaje[6:]

    if apdu_format == "I":
        type_id = asdu[0]
        type_info = asdu_types_df[asdu_types_df['Type'] == type_id]
        if not type_info.empty:
            description = type_info['Description'].values[0]
            reference = type_info['Reference'].values[0]
        else:
            description = reference = "Unknown"
    else:
        description = reference = None

    return {
        "direccion": direccion,
        "start_field": start_field,
        "control_field": control_field,
        "apdu_format": apdu_format,
        "u_type": u_type,
        "asdu": {
            "type_id": type_id,
            "description": description,
            "reference": reference,
            "data": asdu[1:]
        }
    }


def imprimir_resultados(resultados):
    print(f"Dirección: {resultados['direccion']}")
    if "error" in resultados:
        print(f"Análisis: {resultados['error']}")
    else:
        print(f"Análisis:")
        print(f"  Formato APDU: {resultados['apdu_format']}")
        print(f"  Control Field: {resultados['control_field']}")
        if resultados['apdu_format'] == 'I':
            print(f"  ASDU:")
            print(f"    Type ID: {resultados['asdu']['type_id']}")
            print(f"    Descripción: {resultados['asdu']['description']}")
            print(f"    Referencia: {resultados['asdu']['reference']}")
            print(f"    Datos: {resultados['asdu']['data']}")
        elif resultados['apdu_format'] == 'U':
            print(f"  Tipo de mensaje U: {resultados['u_type']}")
    print("--------------------------------------------------")


def analizar_archivo(nombre_archivo):
    with open(nombre_archivo, 'r') as archivo:
        lineas = archivo.readlines()

    secuencias_bytes = []
    direcciones = []
    for linea in lineas:
        pos = linea.find('->')
        if pos != -1:
            direccion = "Enviado"
        else:
            pos = linea.find('<-')
            direccion = "Recibido"
        if pos != -1:
            bytes_hex = linea[pos+2:].strip()
            secuencias_bytes.append(bytes_hex)
            direcciones.append(direccion)

    resultados = []
    for bytes_hex, direccion in zip(secuencias_bytes, direcciones):
        bytes_real = bytes.fromhex(bytes_hex)
        resultado = analizar_iec104(bytes_real, direccion)
        resultados.append(resultado)

    for res in resultados:
        imprimir_resultados(res)

analizar_archivo('traffic_test.txt')
