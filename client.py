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

def bytes_to_hex_string(b):
    return ' '.join(f'{byte:02x}' for byte in b)

def send_startdt_act(client_socket):
    logging.info(f"-> {bytes_to_hex_string(startdt_act)}")
    client_socket.send(startdt_act)

def send_C_IC_NA_1(client_socket,nr,ns):
    ns = ns * 2
    nr = nr * 2
    ns_lsb = ns & 0xFF
    ns_msb = (ns >> 8) & 0xFF
    nr_lsb = nr & 0xFF
    nr_msb = (nr >> 8) & 0xFF
    packet = bytes(bytearray([0x68, 0x04, ns_lsb, ns_msb, nr_lsb, nr_msb, 0x64, 0x01, 0x06, 0x00, 0xff, 0xff, 0x00, 0x00, 0x00, 0x05]))
    logging.info(f"-> {bytes_to_hex_string(packet)}")
    print('C_IC_NA_1 ->', packet)
    client_socket.sendall(packet)

def send_C_CI_NA_1(client_socket,nr,ns):
    ns = ns * 2
    nr = nr * 2
    ns_lsb = ns & 0xFF
    ns_msb = (ns >> 8) & 0xFF
    nr_lsb = nr & 0xFF
    nr_msb = (nr >> 8) & 0xFF
    packet = bytes(bytearray([0x68, 0x0e, ns_lsb, ns_msb, nr_lsb, nr_msb, 0x65, 0x01, 0x06, 0x00, 0xff, 0xff, 0x00, 0x00, 0x00, 0x05]))
    logging.info(f"-> {bytes_to_hex_string(packet)}")
    print('C_CI_NA_1 ->', packet)
    client_socket.sendall(packet)

def send_S_format(client_socket,nr):
    nr = nr * 2
    nr_lsb = nr & 0xFF
    nr_msb = (nr >> 8) & 0xFF
    packet = bytes(bytearray([0x68, 0x04, 0x01, 0x00, nr_lsb, nr_msb]))
    logging.info(f"-> {bytes_to_hex_string(packet)}")
    print('S_format ->', packet)
    client_socket.sendall(packet)

def send_stopdt_act(client_socket):
    logging.info(f"-> {bytes_to_hex_string(stopdt_act)}")
    print("->", stopdt_act)
    client_socket.sendall(stopdt_act)

def listening_thread(client_socket):
    global nr
    global should_continue
    while should_continue:
        received_data = client_socket.recv(1024)
        if received_data != b'':
            if received_data == startdt_act:
                client_socket.sendall(startdt_con)
            logging.info(f"<- {bytes_to_hex_string(received_data)}")
            print('<-', received_data)
            received_data_fields = analizar_iec104(received_data,"<-")
            if received_data_fields["apdu_format"] == 'I' and len(received_data) != 6:
                nr +=1
            
            
def sending_thread(client_socket):
    global nr
    global ns
    global should_continue
    while should_continue:
        send_S_format(client_socket,nr)
        send_C_CI_NA_1(client_socket,nr,ns)
        ns+=1
        send_C_IC_NA_1(client_socket,nr,ns)
        ns+=1
        print('nr:', nr, 'ns',ns,end= '\n\n')
        time.sleep(INTERROGATION_INTERVAL)

should_continue = True
ns=0
nr=0 
SERVER_IP = 'localhost'
SERVER_PORT = 2404
INTERROGATION_INTERVAL = 0.1

def main():
    global should_continue
    start_time = time.time()
    t0=0
    t1=0
    t2=0
    t3=0
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((SERVER_IP, SERVER_PORT))
            send_startdt_act(client_socket)
            if client_socket.recv(1024) == startdt_con:
                print(f"Connected to {SERVER_IP}:{SERVER_PORT}")

            # Crear e iniciar los hilos
            listener = threading.Thread(target=listening_thread, args=(client_socket,))
            sender = threading.Thread(target=sending_thread, args=(client_socket,))  

            listener.start()
            sender.start()

            # Mantener el programa corriendo y esperar una interrupción del teclado (CTRL+C)
            while should_continue:
                time.sleep(1)  # Esperar y no hacer nada, reduciendo la carga de la CPU
            
            # Si sale del bucle, esperar a que los hilos terminen
            listener.join()
            sender.join()

        except KeyboardInterrupt:
            print("Received keyboard interrupt. Stopping threads...")
            should_continue = False
            listener.join()
            sender.join()
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
