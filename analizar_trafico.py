import pandas as pd
from funciones import *

# Constantes para los archivos CSV
ASDU_TYPES_CSV = 'ASDU_types.csv'
COT_VALUES_CSV = 'COT_values.csv'


def analizar_iec104(mensaje, direccion):
    # Inicializar todas las variables que se usan más adelante
    type_id = None
    sq = None
    num_objects = None
    t = None
    pn = None
    cot = None
    org = None
    asdu_address = None
    description = None
    reference = None
    cot_name = None
    cot_abbr = None
    u_type = None
    
    # Cargar DataFrames para los tipos de ASDU y los valores de COT
    asdu_types_df = pd.read_csv(ASDU_TYPES_CSV)
    cot_values_df = pd.read_csv(COT_VALUES_CSV)

    # Constantes
    LONGITUD_DIRECCION = 3

    # Inicialización de variables
    start_field = mensaje[0]
    control_field = mensaje[2]
    cf1 = control_field
    apdu_format = "I" if (cf1 & 0x01) == 0 else "S" if (cf1 & 0x03) == 1 else "U"
    asdu = mensaje[6:]

    # Verificar el campo de inicio
    if start_field != 0x68:
        return {"error": "Campo de inicio inválido", "direccion": direccion}

    # Analizar el formato U
    if apdu_format == "U":
        # Decodificar el tipo de marco U
        u_type = decode_u_type(cf1)

    # Analizar el formato I
    elif apdu_format == "I":
        # Verificar la longitud de ASDU
        if len(asdu) < 6:
            raise Exception("ASDU demasiado corto")

        # Decodificar campos de ASDU
        type_id, sq, num_objects, t, pn, cot, org, asdu_address = decode_asdu_fields(asdu)

        # Obtener información adicional de los DataFrames
        type_info, cot_info, description, reference, cot_name, cot_abbr = get_additional_info(
            asdu_types_df, cot_values_df, type_id, cot)

    # Preparar el resultado
    
    result = prepare_result(direccion, start_field, control_field, apdu_format, u_type, type_id, sq, num_objects,
                            t, pn, cot, org, asdu_address, description, reference, cot_name, cot_abbr)

    return result


def decode_u_type(cf1):
    # Decodificar el tipo de marco U
    u_type_dict = {
        0x43: "Test Frame Activation",
        0x83: "Test Frame Confirmation",
        0x13: "Stop Data Transfer Activation",
        0x23: "Stop Data Transfer Confirmation",
        0x07: "Start Data Transfer Activation",
        0x0B: "Start Data Transfer Confirmation"
    }
    return u_type_dict.get(cf1)


def decode_asdu_fields(asdu):
    # Decodificar campos de ASDU
    type_id = asdu[0]
    second_byte = asdu[1]
    sq = (second_byte & 0x80) >> 7
    num_objects = second_byte & 0x7F
    third_byte = asdu[2]
    t = (third_byte & 0x80) >> 7
    pn = (third_byte & 0x40) >> 6
    cot = third_byte & 0x3F
    org = asdu[3]
    asdu_address = (asdu[4] << 8) | asdu[5]
    return type_id, sq, num_objects, t, pn, cot, org, asdu_address


def get_additional_info(asdu_types_df, cot_values_df, type_id, cot):
    # Obtener información adicional de los DataFrames
    type_info = asdu_types_df[asdu_types_df['Type'] == type_id]
    cot_info = cot_values_df[cot_values_df['Code'] == cot]
    description = reference = cot_name = cot_abbr = None
    if not type_info.empty:
        description = type_info['Description'].values[0]
        reference = type_info['Reference'].values[0]
    if not cot_info.empty:
        cot_name = cot_info['Cause of Transmission'].values[0]
        cot_abbr = cot_info['Abbreviation'].values[0]
    return type_info, cot_info, description, reference, cot_name, cot_abbr


def prepare_result(direccion, start_field, control_field, apdu_format, u_type, type_id, sq, num_objects, t, pn, cot,
                   org, asdu_address, description, reference, cot_name, cot_abbr):
    # Preparar el resultado
    result = {
        "direccion": direccion,
        "start_field": start_field,
        "control_field": control_field,
        "apdu_format": apdu_format,
        "u_type": u_type,
        "asdu": {
            "type_id": type_id,
            "description": description,
            "reference": reference,
            "sq": sq,
            "num_objects": num_objects,
            "t": t,
            "pn": pn,
            "cot": cot,
            "cot_name": cot_name,
            "cot_abbr": cot_abbr,
            "org": org,
            "asdu_address": asdu_address,
        }
    }
    return result
    
def analizar_archivo(nombre_archivo):
    try:
        with open(nombre_archivo, 'r') as archivo:
            lineas = archivo.readlines()
    except FileNotFoundError:
        print(f"El archivo {nombre_archivo} no se encontró.")
        return

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

    for idx,res in enumerate(resultados):
        print(secuencias_bytes[idx])
        imprimir_resultados(res)

analizar_archivo('traffic_test.txt')