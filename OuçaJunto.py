import socket
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import pyaudio
import threading
import numpy as np

#Definindo cores para usar no programa.
# Cores
co0 = "#f0f3f5"
co1 = "#feffff"
co2 = "#3fb5a3"
co3 = "#2e2d2c" #Preto
co4 = "#403d3d" 
co5 = "#4a88e8" 

# Variáveis globais
client_socket = None
stream = None
p = None
client_thread = None
client_running = False
listeners_file = "ouvintes.txt"

#----------------DEFININDO AS FUNÇÕES DE CONEXÃO DE MUSICA E OUVINTES (Em Desenvolvimento)---------------------------------------------------------------------------------

def update_status(new_text):
    status_label.config(text=new_text) 

# Função para iniciar o cliente
def start_client():
    global client_socket, stream, p, client_running, client_thread

    def client_logic():
        global client_socket, stream, p, client_running
        volume = 1.0  # Volume inicial como 100%
        # Conexão para autenticação
        auth_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('10.0.0.110', 65432)
        auth_socket.connect(server_address)
        print(f"Conectado ao servidor para autenticação: {server_address}")

        # Envia o código da sala 
        room_code = input("Digite o código da sala: ")
        auth_socket.sendall(room_code.encode('utf-8'))

        while True:
            response = auth_socket.recv(1024).decode('utf-8')
            print(response)
            if "Código incorreto" in response:
                auth_socket.close()
                return
            if "Outro cliente conectado. Iniciando transmissão de áudio..." in response:
                break

        # Conexão para transmissão de áudio
        client_socket = auth_socket
        print(f"Conectado ao servidor para transmissão de áudio: {server_address}")

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=2, rate=44100, output=True, frames_per_buffer=4096)

        try:
            while client_running:
                try:
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    audio_data = (audio_data * volume).astype(np.int16)
                    stream.write(audio_data.tobytes())
                except OSError as e:
                    print(f"Erro de OSError: {e}")
                    break

        finally:
            stop_client()

    client_running = True
    client_thread = threading.Thread(target=client_logic)
    client_thread.daemon = True
    client_thread.start()

# Função para encerrar o cliente
def stop_client():
    global client_socket, stream, p, client_running

    if client_running:
        client_running = False

        if client_socket:
            client_socket.close()

        if stream:
            stream.stop_stream()
            stream.close()

        if p:
            p.terminate()

        print("Cliente encerrado e recursos liberados.")

#----------------------------------------------Funções da interface (Em Desenvolvimento)-------------------------

#  Função para atualizar o volume e enviar o ajuste para o ouvinte primário
def update_volume(value):
    pass


def on_closing():
    if messagebox.askyesno("Confirmar", "Deseja realmente fechar?"):# Para o servidor, se estiver rodando
        root.destroy()

#----------------FUNÇÕES DE ICONES---------------------------------------------------------------------------------

# Função para redimensionar ícones na interface principal
def resize_icon(image_path, size):
    image = Image.open(image_path)
    resized_image = image.resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(resized_image)

#-------------------------------------INTERFACE GRAFICA (Em Desenvolvimento)-------------------------------------------------------
# Janela de Carregamento 
root = tk.Tk()
root.resizable(False, False)

# Remover barra de título (incluindo botões de minimizar e fechar)
root.overrideredirect(True)

# Centralizar a janela no monitor
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 400
window_height = 300

position_top = int(screen_height / 2 - window_height / 2)
position_right = int(screen_width / 2 - window_width / 2)

root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

# Carregar imagem de fundo
background_image = Image.open("imagens/capadeloading.jpg")  # Substitua pelo caminho da sua imagem
background_image = background_image.resize((400, 300), Image.Resampling.LANCZOS)  # Redimensiona para caber na janela
background_photo = ImageTk.PhotoImage(background_image)

# Criar um Label para a imagem de fundo
background_label = tk.Label(root, image=background_photo)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Barra de progresso
progress = ttk.Progressbar(root, orient="horizontal", length=200, mode="indeterminate")
progress.place(x=100, y=230)  # Posiciona a barra de progresso abaixo do texto

progress.start(10)

# Função para fechar a janela de forma segura
def safe_close():
    if root.winfo_exists():
        # Parar o progresso antes de fechar a janela
        progress.stop()  # Para o incremento da barra de progresso
        root.destroy()

# Fechar a janela após 3 segundos (3000 milissegundos)
root.after(3000, safe_close)

# Mantém a janela aberta até que o carregamento esteja completo
root.mainloop()

# Criando a janela principal (interface principal)
root = tk.Tk()
root.title("OuçaJuntos. Versão: Alpha 0.6")
root.geometry("900x800")
root.configure(background=co2)
root.iconbitmap("imagens/OuçaJuntos.ico")
root.resizable(False, False)

# Adiciona os ícones e redimensiona os ícones na barra de botões da interface principal
try:
    load_icon = resize_icon("imagens/carregarmusica.ico", (32, 32))
    invite_icon = resize_icon("imagens/enviarmusica.ico", (32, 32))
    pause_icon = resize_icon("imagens/pause.ico", (32, 32))
    despause_icon = resize_icon("imagens/despause.ico", (32, 32))
except Exception as e:
    print(f"Erro ao carregar ícones: {e}")
    messagebox.showerror("Erro", "Não foi possível carregar alguns ícones. Verifique o caminho dos arquivos.")

# Criando Menu de Configurações
menu = tk.Menu(root)
root.config(menu=menu)

# Configurando o Menu de Configurações
config_menu = tk.Menu(menu, bg=co5, fg="white")
menu.add_cascade(label="Opções", menu=config_menu)

# Submenu para configuração de ouvintes
listener_submenu = tk.Menu(config_menu, bg=co5, fg="white")
config_menu.add_cascade(label="Configurar Ouvintes", menu=listener_submenu)
listener_submenu.add_command(label="Conectar a uma sala", command=start_client)
listener_submenu.add_command(label="Desconectar da sala", command=stop_client)

# Submenu para Amigos
chat_menu = tk.Menu(config_menu, bg=co5, fg="white")
config_menu.add_cascade(label="Amigos", menu=chat_menu)
chat_menu.add_command(label="Configurar Segundo Ouvinte")

# Controle de playlist
playlist = tk.Listbox(root)
playlist.grid(row=0, column=0, columnspan=4, padx=10, pady=5, sticky='nsew')


# Botões da interface principal
load_button = tk.Button(root, image=load_icon)
load_button.grid(row=1, column=0, padx=5, pady=5)

send_button = tk.Button(root, image=invite_icon)
send_button.grid(row=1, column=1, padx=5, pady=5)

pause_button = tk.Button(root, image=pause_icon)
pause_button.grid(row=1, column=2, padx=5, pady=5)

resume_button = tk.Button(root, image=despause_icon)
resume_button.grid(row=1, column=3, padx=5, pady=5)

# Controle deslizante de volume
volume_slider = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, command=update_volume, bg=co2, label="Volume Local:")
volume_slider.set(100)  # Define o volume inicial como 100%
volume_slider.grid(row=3, column=0, columnspan=4, padx=10, pady=5, sticky='ew')

# Rótulo de status
status_label = tk.Label(root, text="Aguardando configuração...", bg="lightgrey", fg="black", font=("Helvetica", 12))
status_label.grid(row=4, column=0, columnspan=4, pady=5, sticky='ew')

# Ajusta o peso das colunas e linhas para expandir conforme necessário
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=0)
root.grid_rowconfigure(2, weight=0)
root.grid_rowconfigure(3, weight=0)

#----------------------Executores----------------------------------------------------------

# Configura o protocolo para tratar o fechamento de todo programa
root.protocol("WM_DELETE_WINDOW", on_closing)

# Executor de todas as interfaces gráficas
root.mainloop()

##PROGRAMA EM DESENVOLVIVMENTO. V:0.6