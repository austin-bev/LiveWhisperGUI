#Sockets + Threads
import socket
import threading
#Model
from faster_whisper import WhisperModel
#Performance testing
import time
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)
logging.getLogger("faster_whisper").setLevel(logging.DEBUG)

Model = 'tiny'      # Whisper model size (tiny, base, small, medium, large)
English = True      # Use English-only model?
Translate = False   # Translate non-English to English?
GPU = False

model = WhisperModel(Model, device="gpu" if GPU else "cpu", compute_type="int8")

def handle_connection(connection):
    while True:
        # Wait for a response from the whisper client
        data = connection.recv(1024)
        start_time = time.time()  # record the start time
        # If there is no more data to receive, break out of the loop
        if not data:
            break

        # Send a response back to file 1
        segments, info = model.transcribe('dictate.wav',language='en' if English else '',task='translate' if Translate else 'transcribe')

        sentence = ''
        for segment in segments:
            sentence += segment.text
            #print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
        connection.sendall(sentence.encode())
        end_time = time.time()  # record the end time
        execution_time = end_time - start_time  # calculate the execution time
        logging.debug(f"Whisper model execution time: {execution_time:.6f} seconds")
    # Close the connection
    connection.close()

def respond_request():
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to a public host, and a well-known port where the whisper client will connect
    server_address = ('localhost', 9999)
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(5)
    logging.info("Whisper server ready to accept requests")

    while True:
        # Wait for a connection
        connection, client_address = sock.accept()

        # Create a thread to handle the connection
        connection_thread = threading.Thread(target=handle_connection, args=(connection,))
        connection_thread.start()

if __name__ == '__main__':
    respond_request()