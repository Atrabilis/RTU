import os
import sys
sys.path.insert(0, os.getcwd())
from iec104_control_frames import *
import socket
import time

# Configuración del servidor (RTU)
SERVER_IP = 'localhost'  # Cambia esto a la IP del servidor si es necesario
SERVER_PORT = 2404

def bytes_a_decimal(bytes_cadena):
    return ' '.join(str(b) for b in bytes_cadena)


# Crear un socket TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Conectarse al servidor
    s.connect((SERVER_IP, SERVER_PORT))
    
    # STARTDT Act: 
    s.sendall(startdt_act)
    
    # Recibir la respuesta del servidor (STARTDT Con)
    data = s.recv(1024)
    if data == startdt_con:
        print('Conexión aceptada y transmisión de datos iniciada.')
    else:
        print('Respuesta inesperada del servidor.')
    
    # TESTFR Act:
    s.sendall(testfr_act)
    data = s.recv(1024)
    if data == testfr_con:
        print('Test Frame succesful')
    else:
        print('Respuesta inesperada del servidor.')
    
    #STOPDT act
    s.sendall(stopdt_act)
    # Recibir la respuesta del servidor (STOPDT Con)
    data = s.recv(1024)
    if data == stopdt_con:
        print('Conexión y transmisión de datos Terminado satisfactoriamente.')
    else:
        print('Respuesta inesperada del servidor.')
