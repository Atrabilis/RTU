import os
import sys
from iec104_control_frames import *
sys.path.insert(0, os.getcwd())

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
