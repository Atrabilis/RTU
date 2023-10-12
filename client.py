import threading
import socket
import time
import logging
import time
from funciones import *
from analizar_trafico import *
from iec104_control_frames import *
from pymongo import MongoClient
import queue

data_queue = queue.Queue()

mongoclient = MongoClient('localhost', 27017)
db = mongoclient.datosRTU
collection= db.datos
should_continue = True
ns=0
nr=0 
SERVER_IP = 'localhost'
SERVER_PORT = 2404
INTERROGATION_INTERVAL = 1

# Configurar el logging
logging.basicConfig(filename='communication_log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def is_mongo_alive():
    try:
        # Intenta obtener un documento de la colección (limitado a 1 para no cargar demasiados datos).
        collection.find_one()
        return True
    except Exception as e:
        print(f"Error al conectar con MongoDB: {str(e)}")
        return False

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
            #print(received_data_fields)
            data_queue.put(received_data_fields)

def database_insertion_thread():
    while should_continue:
        try:
            # Tomar datos de la cola y realizar la inserción en MongoDB
            data_to_insert = data_queue.get(timeout=1)  # Timeout para evitar bloqueo y poder cerrar el hilo adecuadamente
            
            # Convertir numpy.ndarray a lista
            data_to_insert['asdu']['information_object_format'] = data_to_insert['asdu']['information_object_format'].tolist()
            
            # Insertar datos en MongoDB
            collection.insert_one(data_to_insert)
        except queue.Empty:
            pass  # No hacer nada si la cola está vacía, simplemente continuar y volver a intentarlo
            
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


def main():
    global should_continue
    start_time = time.time()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((SERVER_IP, SERVER_PORT))
            send_startdt_act(client_socket)
            if client_socket.recv(1024) == startdt_con:
                print(f"Connected to {SERVER_IP}:{SERVER_PORT}")

            # Crear e iniciar los hilos
            listener = threading.Thread(target=listening_thread, args=(client_socket,))
            sender = threading.Thread(target=sending_thread, args=(client_socket,))
            db_inserter = threading.Thread(target=database_insertion_thread)  # Hilo para inserciones en MongoDB

            listener.start()
            sender.start()
            db_inserter.start()

            # Mantener el programa corriendo y esperar una interrupción del teclado (CTRL+C)
            while should_continue:
                time.sleep(1)  # Esperar y no hacer nada, reduciendo la carga de la CPU
            
            # Si sale del bucle, esperar a que los hilos terminen
            listener.join()
            sender.join()
            db_inserter.join()

        except KeyboardInterrupt:
            print("Received keyboard interrupt. Stopping threads...")
            should_continue = False  # Primero, asegurarte de que los threads sepan que deben parar
            db_inserter.join()
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
