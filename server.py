#!/usr/bin/python3

import datetime
import numpy as np
import signal
import socket
import string
import sys
from _thread import *

# --- R4vN Challenge Configuration ---

# The secret flag
FLAG = "theblackravenholdsencryptedsecrets" 

# Alphabet used for encryption (25 characters: a-y)
ALPHABET = string.ascii_lowercase[:-1] 
SIZE = len(ALPHABET)

# 5x5 Encryption Matrix
KEY_MATRIX = np.array([
    [23,  3,  5,  7, 16],
    [22, 15,  0, 14, 19],
    [ 6,  8, 12, 21,  1],
    [17, 13, 20, 24,  4],
    [ 9, 18, 10, 11,  2]
], dtype=int)
DIM = 5

def encrypt(msg: str, key: np.array):
    # Filter: keep only characters present in the alphabet (a-y)
    msg_clean = "".join([c for c in msg.lower() if c in ALPHABET])
    
    # Split the message into chunks of size 5
    splitted = [msg_clean[i:i + DIM] for i in range(0, len(msg_clean), DIM)]
    encrypted = ''
    a = ord('a')
    for chunk in splitted:
        # Add 'a' as padding if the chunk is smaller than DIM
        chunk += 'a' * (DIM - len(chunk))
        vect = np.array([ord(c) - a for c in chunk])
        # Matrix-vector multiplication modulo 25
        encrypted += ''.join([ALPHABET[m % SIZE] for m in key.dot(vect)])
    return encrypted

# English Welcome Message
WELCOME = """Welcome to the R4vN Sanctuary. Here is the secret message to decrypt: %s
To assist you, a cryptographic oracle is available to encrypt your own messages.
"""

# --- Server Logic ---

SOCKET_HOST = "0.0.0.0"
SOCKET_PORT = 50001

def serverlog(msg):
    print(f"[{datetime.datetime.now()}] {msg}")

def client_handler(connection, client):
    # Encrypt the flag at the start of the connection
    ciphertext = encrypt(FLAG, KEY_MATRIX)
    connection.send((WELCOME % ciphertext).encode())
    
    while True:
        try: 
            connection.send("\nEnter the message you wish to encrypt: ".encode())
            data = connection.recv(1024).decode().strip()
            if not data: break
            
            # Input validation
            if not all(c in ALPHABET for c in data):
                connection.send("Invalid character! Please use only lowercase letters (a-y).\n".encode())
            else:
                ct = f"Encrypted message: {encrypt(data, KEY_MATRIX)}\n"
                connection.send(ct.encode())
        except: 
            break
    connection.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Enable address reuse to avoid "Address already in use" errors
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((SOCKET_HOST, SOCKET_PORT))
    server.listen(5)
    serverlog(f"R4vN Challenge server started on: {SOCKET_HOST}:{SOCKET_PORT}")
    
    while True:
        conn, addr = server.accept()
        serverlog(f"New connection from: {addr[0]}:{addr[1]}")
        start_new_thread(client_handler, (conn, f"{addr[0]}:{addr[1]}"))

if __name__ == "__main__":
    start_server()
