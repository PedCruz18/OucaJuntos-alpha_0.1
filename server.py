import socket
import threading
import wave
import os
import time

# Código da sala
ROOM_CODE = "12345"
authenticated_clients = []
lock = threading.Lock()

def wavfilesverific():
    music_folder = "musicas"
    wav_files = [f for f in os.listdir(music_folder) if f.endswith('.wav')]

    if not wav_files:
        print("------------------!AVISO!--------------------------")
        print("Nenhum arquivo WAV encontrado na pasta 'musicas'.")
        print("---------------------------------------------------")
    else:
        print(f"Musicas Importadas: {wav_files}")
        print("---------------------------------------------------")

# Função para transmitir o áudio WAV para os clientes
def stream_audio(clients):
    music_folder = "musicas"
    wav_files = [f for f in os.listdir(music_folder) if f.endswith('.wav')]

    if not wav_files:
        print("------------------!AVISO!--------------------------")
        print("Nenhum arquivo WAV encontrado na pasta 'musicas'.")
        print("---------------------------------------------------")
        return

    time.sleep(1)
    for wav_file in wav_files:
        file_path = os.path.join(music_folder, wav_file)
        print("")
        print("---------Iniciando Transmissão---------------------------")
        print(f"Tocando {wav_file}...")

        with wave.open(file_path, 'rb') as wf:
            chunk_size = 4096
            data = wf.readframes(chunk_size)
            while data:
                with lock:
                    for client_conn in clients:
                        try:
                            client_conn.sendall(data)
                        except Exception as e:
                            print("------------------!AVISO!--------------------------")
                            print(f"Erro ao enviar dados para o cliente: {e}")
                            print("---------------------------------------------------")
                            clients.remove(client_conn)
                data = wf.readframes(chunk_size)

    print("Todos os arquivos foram transmitidos.")
    authenticated_clients.clear()
    print(f"lista de clientes limpa > {authenticated_clients}")
    print("---------------------------------------------------")

def handle_auth(connection, client_address):
    print(f"Conexão de autenticação estabelecida com: {client_address}")

    try:
        # Solicita o código da sala ao cliente
        connection.sendall("".encode('utf-8'))
        room_code = connection.recv(1024).decode().strip()

        if room_code == ROOM_CODE:
            with lock:
                authenticated_clients.append(connection)
                if len(authenticated_clients) == 1:
                    connection.sendall("...\n".encode('utf-8'))
                    connection.sendall(f"Você entrou na Sala {ROOM_CODE}.\n".encode('utf-8'))
                    connection.sendall("Aguardando outro cliente se conectar..\n".encode('utf-8'))
                    connection.sendall("--------------------------------------\n".encode('utf-8'))
                elif len(authenticated_clients) == 2 :
                    for client in authenticated_clients:
                        client.sendall("Outro cliente conectado. Iniciando transmissão de áudio...\n".encode('utf-8'))
                    threading.Thread(target=stream_audio, args=(authenticated_clients.copy(),)).start()
        else:
            connection.sendall("Código incorreto. Conexão encerrada.\n".encode('utf-8'))
            connection.close()

    except socket.error as e:
        print(f"Cliente {client_address} se desconectou")
        connection.close()

    finally:
        for client in authenticated_clients:
            print("")
            print("--------------------------------------")
            print(f"Cliente {client_address} passou pela autenticação")
            print("Lista de Clientes autenticados:")
            print(client.getpeername())
            print("--------------------------------------")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('10.0.0.110', 65432)
    server_socket.bind(server_address)
    server_socket.listen(5)
    print(f"Servidor ouvindo em {server_address[0]}:{server_address[1]}")
    print("---------------------------------")
    wavfilesverific()
    

    try:
        while True:
            connection, client_address = server_socket.accept()
            client_thread = threading.Thread(target=handle_auth, args=(connection, client_address))
            client_thread.start()
    
    except Exception as e:
        print(f"Erro no servidor: {e}")
    
    finally:
        server_socket.close()

print("")
print("Sala de Musicas para Testes")
print("---------------------------------")
start_server()
