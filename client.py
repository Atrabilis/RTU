import threading
import socket
import time
import logging
import time
from funciones import *
from analizar_trafico import *
from iec104_control_frames import *


# Configurar el logging
logging.basicConfig(filename='communication_log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def send_startdt_act(client_socket):
    logging.info(f"-> {startdt_act}")
    client_socket.send(startdt_act)

def send_C_IC_NA_1(client_socket, nr, ns):
    ns = ns * 2
    nr = nr * 2
    ns_lsb = ns & 0xFF
    ns_msb = (ns >> 8) & 0xFF
    nr_lsb = nr & 0xFF
    nr_msb = (nr >> 8) & 0xFF
    packet = bytearray([0x68, 0x04, ns_lsb, ns_msb, nr_lsb, nr_msb, 0x64, 0x01, 0x06, 0x00, 0x01, 0x00])
    logging.info(f"-> {packet}")
    print('->', packet)
    client_socket.sendall(packet)

def send_C_CI_NA_1(client_socket, nr, ns):
    ns = ns * 2
    nr = nr * 2
    ns_lsb = ns & 0xFF
    ns_msb = (ns >> 8) & 0xFF
    nr_lsb = nr & 0xFF
    nr_msb = (nr >> 8) & 0xFF
    packet = bytearray([0x68, 0x0e, ns_lsb, ns_msb, nr_lsb, nr_msb, 0x65, 0x01, 0x06, 0x00, 0xff, 0xff, 0x00, 0x00, 0x00, 0x05])
    logging.info(f"-> {packet}")
    print('->', packet)
    client_socket.sendall(packet)

def send_stopdt_act(client_socket):
    logging.info(f"-> {stopdt_act}")
    print("->", stopdt_act)
    client_socket.sendall(stopdt_act)

def listening_thread(client_socket):
    while True:
        received_data = client_socket.recv(1024)
        if received_data != b'':
            logging.info(f"Received: {received_data}")
            print('<-', received_data)
            
def sending_thread(client_socket, ns, nr):
    while True:
        #send_C_CI_NA_1(client_socket,nr,ns)
        #ns+=1
        #nr+=1
        client_socket.sendall(b'\x68\x04\x83\x00\x00\x00')
        time.sleep(INTERROGATION_INTERVAL)

SERVER_IP = 'localhost'
SERVER_PORT = 2404
INTERROGATION_INTERVAL = 1

def main():
    start_time = time.time()
    t0=0
    t1=0
    t2=0
    t3=0
    ns=0
    nr=0
    start_time = time.time()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((SERVER_IP, SERVER_PORT))
            send_startdt_act(client_socket)
            if client_socket.recv(1024) == startdt_con:
                print(f"Connected to {SERVER_IP}:{SERVER_PORT}")

            # Crear e iniciar los hilos
            listener = threading.Thread(target=listening_thread, args=(client_socket,))
            sender = threading.Thread(target=sending_thread, args=(client_socket, 0, 0))  # ns y nr iniciales a 0

            listener.start()
            sender.start()

            # Mantener el programa en ejecución
            while True:
                time.sleep(1)

        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            print(f"An error occurred: {str(e)}")
        finally:
            end_time = time.time()
            connection_duration = end_time-start_time
            logging.info(f"Connection duration: {connection_duration:.2f} seconds")
            print(f"Connection duration: {connection_duration:.2f} seconds")

if __name__ == "__main__":
    main()
