import os
import sys
from iec104_control_frames import *
sys.path.insert(0, os.getcwd())

def bytes_a_decimal(bytes_cadena):
    return ' '.join(str(b) for b in bytes_cadena)

def iniciar_conexion(s,SERVER_IP,SERVER_PORT):
# Conectarse al servidor
    s.connect((SERVER_IP, SERVER_PORT))
    
    # STARTDT Act: 
    s.sendall(startdt_act)
    print("T-> " + str(startdt_act) + "START ACT")

    # Recibir la respuesta del servidor (STARTDT Con)
    data = s.recv(1024)
    if data == startdt_con:
        print("R<- " + str(startdt_con) + "START CON")
        print('Conexión aceptada y transmisión de datos iniciada.')
    else:
        print('Respuesta inesperada del servidor.')

def detener_conexion_socket(s):
    #STOPDT act
    s.sendall(stopdt_act)
    # Recibir la respuesta del servidor (STOPDT Con)
    data = s.recv(1024)
    if data == stopdt_con:
        print('Desconexion de socket satisfactorio')
    else:
        print('Respuesta inesperada del servidor.')

def test_conection(s):
    s.sendall(testfr_act)
    print("T-> "+str(testfr_act)+  " TESTFR ACT")
    data= s.recv(1024)
    if data == testfr_con:
        print("R<- "+str(testfr_act) + " TESTFR CON")
        print("conexión normal")
    else:
        detener_conexion_socket(s)
