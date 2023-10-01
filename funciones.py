import os
import sys
from iec104_control_frames import *
sys.path.insert(0, os.getcwd())

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
            print(f"    Descripción ID: {resultados['asdu']['description']}")
            print(f"    Referencia ID: {resultados['asdu']['reference']}")
            print(f"    SQ: {resultados['asdu']['sq']}")
            print(f"    Number of Objects: {resultados['asdu']['num_objects']}")
            print(f"    T: {resultados['asdu']['t']}")
            print(f"    PN: {resultados['asdu']['pn']}")
            print(f"    COT: {resultados['asdu']['cot']}")
            print(f"    Nombre COT: {resultados['asdu']['cot_name']}")
            print(f"    Abreviación COT: {resultados['asdu']['cot_abbr']}")
            print(f"    ORG: {resultados['asdu']['org']}")
            print(f"    ASDU Address: {resultados['asdu']['asdu_address']}")
            print(f"    information elements len: {resultados['asdu']['element_len']}")
            
            for i,j in enumerate(resultados['asdu']['info_objects']):
                print(f"Object {i}: {j}")
        
        elif resultados['apdu_format'] == 'U':
            print(f"  Tipo de mensaje U: {resultados['u_type']}")

    print("--------------------------------------------------")



def interpretar_objetos_informacion(data, sq, num_objects, apdu_length):
    index = 0  # índice para rastrear la posición actual en los datos
    objetos = []

    LONGITUD_DIRECCION = 3  # Longitud del campo de dirección del objeto de información

    if sq == 0:
        # Para sq = 0, calculamos la longitud del objeto de información usando la fórmula dada
        longitud_objeto = (apdu_length - 10) // num_objects - LONGITUD_DIRECCION
        while index < len(data):
            direccion_objeto = data[index:index+LONGITUD_DIRECCION]
            index += LONGITUD_DIRECCION
            elementos_informacion = data[index:index+longitud_objeto]
            index += longitud_objeto
            objetos.append({
                "direccion": direccion_objeto,
                "elementos": elementos_informacion
            })
    elif sq == 1:
        # Para sq = 1, calculamos la longitud del objeto de información usando la fórmula dada
        longitud_objeto = apdu_length - 13  # Calculado según la fórmula proporcionada
        longitud_elemento = longitud_objeto // num_objects  # Longitud de cada elemento de información
        direccion_objeto_base = int.from_bytes(data[index:index+LONGITUD_DIRECCION], byteorder='little')
        index += LONGITUD_DIRECCION
        for i in range(num_objects):
            elementos_informacion = data[index:index+longitud_elemento]
            index += longitud_elemento
            direccion_objeto = (direccion_objeto_base + i).to_bytes(LONGITUD_DIRECCION, byteorder='little')
            objetos.append({
                "direccion": direccion_objeto,
                "elementos": elementos_informacion
            })

    return objetos

ELEMENT_LENGTHS = {
    "SIQ": 1,
    "DIQ": 1,
    "BSI": 4,
    "SCD": 4,
    "QDS": 1,
    "VTI": 1,
    "NVA": 2,
    "SVA": 2,
    "IEEE STD 754": 4,
    "BCR": 5,
    "SEP": 1,
    "SPE": 1,
    "OCl": 1,
    "QDP": 1,
    "SCO": 1,
    "DCO": 1,
    "RCO": 1,
    "CP56Time2a": 7,
    "CP24Time2a": 3,
    "CP16Time2a": 2,
    "QOI": 1,
    "QCC": 1,
    "QPM": 1,
    "QPA": 1,
    "QRP": 1,
    "QOC": 1,
    "QOS": 1,
    "FRQ": 1,
    "SRQ": 1,
    "SCQ": 1,
    "LSQ": 1,
    "AFQ": 1,
    "NOF": 2,
    "NOS": 2,
    "LOF": 3,
    "LOS": 1,
    "CHS": 1,
    "SOF": 1,
    "COI": 2,
    "FBP": 2
}

ASDU_FORMATS = {
    1: ["SIQ"],
    2: ["SIQ", "CP24Time2a"],
    3: ["DIQ"],
    4: ["DIQ", "CP24Time2a"],
    5: ["VTI", "QDS"],
    6: ["VTI", "QDS", "CP24Time2a"],
    7: ["BSI", "QDS"],
    8: ["BSI", "QDS", "CP24Time2a"],
    9: ["NVA", "QDS"],
    10: ["NVA", "QDS", "CP24Time2a"],
    11: ["SVA", "QDS"],
    12: ["SVA", "QDS", "CP24Time2a"],
    13: ["IEEE STD 754", "QDS"],
    14: ["IEEE STD 754", "QDS", "CP24Time2a"],
    15: ["BCR"],
    16: ["BCR", "CP24Time2a"],
    17: ["CP16Time2a", "CP24Time2a"],
    18: ["SEP", "QDP", "CP16Time2a", "CP24Time2a"],
    19: ["OCl", "QDP", "CP16Time2a", "CP24Time2a"],
    20: ["SCD", "QDS"],
    21: ["NVA"],
    30: ["SIQ", "CP56Time2a"],
    31: ["DIQ", "CP56Time2a"],
    32: ["VTI", "QDS", "CP56Time2a"],
    33: ["BSI", "QDS", "CP56Time2a"],
    34: ["NVA", "QDS", "CP56Time2a"],
    35: ["SVA", "QDS", "CP56Time2a"],
    36: ["IEEE STD 754", "QDS", "CP56Time2a"],
    37: ["BCR", "CP56Time2a"],
    38: ["CP16Time2a", "CP56Time2a"],
    39: ["SEP", "QDP", "CP16Time2a", "CP56Time2a"],
    40: ["OCl", "QDP", "CP16Time2a", "CP56Time2a"],
    45: ["SCO"],
    46: ["DCO"],
    47: ["RCO"],
    48: ["NVA", "QOS"],
    49: ["SVA", "QOS"],
    50: ["IEEE STD 754", "QOS"],
    51: ["BSI"],
    58: [],
    59: [],
    60: [],
    61: [],
    62: [],
    63: [],
    64: [],
    70: ["COI"],
    100: ["QOI"],
    101: ["QCC"],
    102: [],
    103: ["CP56Time2a"],
    104: ["FBP"],
    105: ["QRP"],
    106: ["CP16Time2a"],
    107: [],
    110: ["NVA", "QPM"],
    111: ["SVA", "QPM"],
    112: ["IEEE STD 754", "QPM"],
    113: ["QPA"],
    120: ["NOF", "LOF", "FRQ"],
    121: ["NOF", "NOS", "LOF", "SRQ"],
    122: ["NOF", "NOS", "SCQ"],
    123: ["NOF", "NOS", "LSQ", "CHS"],
    124: ["NOF", "NOS", "AFQ"],
    125: ["NOF", "NOS", "LOS"],
    126: ["NOF", "LOF", "SOF", "CP56Time2a"],
    127: []
}

def send_gnrl_interrogation_apdu(client_socket, increment):
    # Incrementar el quinto byte en el APDU
    interrogation_apdu = bytearray(b'\x68\x04\x01\x00\x00\x00')
    interrogation_apdu[4] = (interrogation_apdu[4] + increment) & 0xFF  # Incrementa el quinto byte

    # Send the Interrogation General APDU
    client_socket.send(interrogation_apdu)
    print("T->", interrogation_apdu)
    
def send_ctr_interrogation_apdu(client_socket, increment):
    # Incrementar el quinto byte en el APDU
    interrogation_apdu = bytearray(b'\x68\x0e\x00\x00\x00\x00\x65\x01\x06\x00\xff\xff\x00\x00\x00\x05')
    interrogation_apdu[2] = (interrogation_apdu[4] + increment) & 0xFF
    interrogation_apdu[4] = (interrogation_apdu[4] + increment) & 0xFF  # Incrementa el quinto byte

    # Send the Interrogation General APDU
    client_socket.send(interrogation_apdu)
    print("T->", interrogation_apdu)

def bytes_a_decimal(bytes_cadena):
    return ' '.join(str(b) for b in bytes_cadena)

def iniciar_conexion(s,SERVER_IP,SERVER_PORT):
# Conectarse al servidor
    # STARTDT Act: 
    s.sendall(startdt_act)
    
    # Recibir la respuesta del servidor (STARTDT Con)
    data = s.recv(1024)
    if data == startdt_con:
        print('Conexión aceptada y transmisión de datos iniciada.')
    else:
        print('Respuesta inesperada del servidor.')

def detener_conexion_socket(s):
    #STOPDT act
    s.sendall(stopdt_act)
    # Recibir la respuesta del servidor (STOPDT Con)
    data = s.recv(1024)
    if data == stopdt_con:
        print('Conexión y transmisión de datos Terminado satisfactoriamente.')
    else:
        print('Respuesta inesperada del servidor.')

def probar_conexion(s):
    s.send(testfr_act)
    data = s.recv(1024)
    if data == testfr_con:
        print("comunicacion OK")
    else:
        print('Respuesta inesperada del servidor.')
        detener_conexion_socket(s)

def analizar_iec104(mensaje):
    """
    Analiza una secuencia de bytes de un mensaje IEC 104.
    
    :param mensaje: Secuencia de bytes del mensaje IEC 104 a analizar.
    :type mensaje: bytes
    :return: Un diccionario con la información analizada del mensaje.
    :rtype: dict
    """
    # Verificar la longitud del mensaje
    if len(mensaje) < 7:
        return "Mensaje demasiado corto"
    
    # Extraer el campo de inicio (primer byte)
    start_field = mensaje[0]
    
    # Extraer el campo de longitud (segundo byte)
    length_field = mensaje[1]
    
    # Extraer el campo de control (bytes del 3 al 7)
    control_field = mensaje[2:7]
    
    # Determinar el formato de la APDU
    cf1_last_two_bits = control_field[0] & 0b11  # Extraer los dos últimos bits del CF1
    if cf1_last_two_bits == 0b00:
        apdu_format = 'I'
    elif cf1_last_two_bits == 0b01:
        apdu_format = 'S'
    elif cf1_last_two_bits == 0b11:
        apdu_format = 'U'
    else:
        apdu_format = 'Desconocido'
    
    # Determinar el tipo de mensaje U
    u_type = None
    if apdu_format == 'U':
        u_type_values = {
            0x43: 'Test Frame Activation',
            0x83: 'Test Frame Confirmation',
            0x13: 'Stop Data Transfer Activation',
            0x23: 'Stop Data Transfer Confirmation',
            0x07: 'Start Data Transfer Activation',
            0x0B: 'Start Data Transfer Confirmation'
        }
        u_type = u_type_values.get(control_field[0], 'Desconocido')
    
    # Extraer el campo de datos
    data = mensaje[7:]
    
    info = {
        'start_field': start_field,
        'length_field': length_field,
        'control_field': control_field,
        'apdu_format': apdu_format,
        'u_type': u_type,
        'data': data,
    }
    
    return info

#print(analizar_iec104(b'\x68\x14\x00\x00\x00\x00\x67\x01\x06\x00\xff\xff\x00\x00\x00\x6d\xbe\x21\x11\x1c\x09\x17'))
#print(analizar_iec104(b'\x68\x14\x00\x00\x00\x00\x67\x01\x06\x00\xff\xff\x00\x00\x00\x6d\xbe\x21\x11\x1c\x09\x17'))
