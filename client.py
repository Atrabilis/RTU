import os
import sys
sys.path.insert(0, os.getcwd())
from iec104_control_frames import *
import socket
import time
from funciones import *

# Configuración del servidor (RTU)
SERVER_IP = 'localhost'  # Cambia esto a la IP del servidor si es necesario
SERVER_PORT = 2404

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    iniciar_conexion(s,SERVER_IP,SERVER_PORT)
    test_conection(s)
    
       
    
