import socket
import time
from funciones import *

# Configuration for the server (RTU)
SERVER_IP = 'localhost'  # Change this to the RTU's IP address
SERVER_PORT = 2404

# Configure the T3 time for the interrogation
INTERROGATION_INTERVAL = 1  # 60 seconds (adjust as needed)

def send_interrogation_apdu(client_socket, increment):
    # Incrementar el quinto byte en el APDU
    interrogation_apdu = bytearray(b'\x68\x04\x01\x00\x00\x00')
    interrogation_apdu[4] = (interrogation_apdu[4] + increment) & 0xFF  # Incrementa el quinto byte

    # Send the Interrogation General APDU
    client_socket.send(interrogation_apdu)

def main():
    start_time = time.time()  # Record the start time
    incremento = 0  # Inicializar el incremento en 0

    # Create a socket for the client
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            # Connect to the server (RTU)
            client_socket.connect((SERVER_IP, SERVER_PORT))
            iniciar_conexion(client_socket, SERVER_IP, SERVER_PORT)
            print(f"Connected to {SERVER_IP}:{SERVER_PORT}")
            time.sleep(1)
            while True:
                # Send the Interrogation General APDU with the current incremento
                send_interrogation_apdu(client_socket, incremento)

                # Receive data from the RTU
                received_data = client_socket.recv(1024)  # Adjust the buffer size as needed

                # Process or print the received data as needed
                print(f"Received data: {received_data}")  # Assuming UTF-8 encoding

                # Incrementar el valor del incremento
                incremento += 2

                # Sleep for the interrogation interval before sending the next APDU
                time.sleep(INTERROGATION_INTERVAL)

        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            end_time = time.time()  # Record the end time when the connection ends
            connection_duration = end_time - start_time
            print(f"Connection duration: {connection_duration} seconds")

if __name__ == "__main__":
    main()
