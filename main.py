from machine import Pin
import network
import socket
import time

# ==============================================================================
# 1. CONFIGURAÇÕES GERAIS E MAPEAMENTO (Ativo em LOW)
# ==============================================================================
SSID = "ESP_SANTANA"
PASSWORD = "12345678"
DOMAIN_NAME = "fungicos"  # Permite acessar via http://fungicos.local

# Configuração dos pinos com dicionário para manter o código limpo
dispositivos = {
    "ar":      {"pin": Pin(21, Pin.OUT, value=1), "nome": "Ar Condicionado"},
    "cozinha": {"pin": Pin(22, Pin.OUT, value=1), "nome": "Luz Cozinha"},
    "sala":    {"pin": Pin(13, Pin.OUT, value=1), "nome": "Luz Sala"},
    "externa": {"pin": Pin(25, Pin.OUT, value=1), "nome": "Luzes Externas"}
}

# ==============================================================================
# 2. INICIALIZAÇÃO DO WI-FI E CONFIGURAÇÃO DE DOMÍNIO (mDNS)
# ==============================================================================
# Define o nome de rede do ESP32 antes de ativar o sinal
try:
    network.hostname(DOMAIN_NAME)
except AttributeError:
    pass  # Garante compatibilidade caso a versão mude

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(
    essid=SSID,
    password=PASSWORD,
    authmode=network.AUTH_WPA_WPA2_PSK
)

while not ap.active():
    time.sleep(0.5)

print("\n======================================")
print(f"Wi-Fi Ativo: {SSID}")
print(f"Endereço IP: {ap.ifconfig()[0]}")
print(f"Acesso via Domínio: http://{DOMAIN_NAME}.local")
print("======================================\n")

# ==============================================================================
# 3. INTERFACE WEB COM PLANTA BAIXA EM CSS GRID
# ==============================================================================
def html_dashboard():
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fungicos Home Control</title>
    <style>
        :root {
            --bg-body: #0f172a;
            --bg-blueprint: #020617;
            --bg-room: #1e293b;
            --border: #334155;
            --btn-on: #22c55e;
            --btn-off: #ef4444;
            --text-main: #f8fafc;
            --accent: #38bdf8;
        }
        body {
            background-color: var(--bg-body);
            color: var(--text-main);
            font-family: 'Segoe UI', Roboto, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
        }
        .container {
            width: 100%;
            max-width: 600px;
            text-align: center;
        }
        h1 {
            margin-bottom: 2px;
            font-size: 26px;
            color: var(--accent);
        }
        .url-hint {
            color: #64748b;
            font-size: 13px;
            margin-bottom: 25px;
        }
        
        /* Container que simula a Planta Baixa da Casa */
        .planta-baixa {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            background-color: var(--bg-blueprint);
            padding: 20px;
            border-radius: 24px;
            border: 3px dashed var(--border);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
        }
        
        /* Estilização das Divisões dos Cômodos */
        .comodo {
            background-color: var(--bg-room);
            border: 2px solid var(--border);
            border-radius: 16px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
            min-height: 120px;
            transition: border-color 0.2s;
        }
        .comodo:hover {
            border-color: var(--accent);
        }
        
        /* Customização para a Área Externa ocupar o rodapé inteiro da planta */
        .area-externa {
            grid-column: span 2;
            min-height: 90px;
        }
        
        .titulo-comodo {
            font-size: 15px;
            font-weight: 600;
            color: #e2e8f0;
            margin-top: 0;
            margin-bottom: 15px;
        }
        
        /* Elementos de Controle */
        .botoes {
            display: flex;
            gap: 8px;
        }
        button {
            border: none;
            width: 85px;
            height: 38px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: bold;
            cursor: pointer;
            color: white;
            transition: transform 0.1s, opacity 0.2s;
        }
        button:active {
            transform: scale(0.95);
        }
        .on { background-color: var(--btn-on); }
        .off { background-color: var(--btn-off); }
        
        /* Responsividade para telas muito pequenas */
        @media (max-width: 450px) {
            .planta-baixa { grid-template-columns: 1fr; }
            .area-externa { grid-column: span 1; }
        }
    </style>
</head>
<body>
<div class="container">
    <h1>🍄 Fungicos Home Control</h1>
    <div class="url-hint">Acesse por: http://fungicos.local</div>
    
    <div class="planta-baixa">
    
        <div class="comodo">
            <div class="titulo-comodo">🛏️ Quarto (Ar Cond.)</div>
            <div class="botoes">
                <a href="/ar/on"><button class="on">LIGAR</button></a>
                <a href="/ar/off"><button class="off">DESLIGAR</button></a>
            </div>
        </div>
        
        <div class="comodo">
            <div class="titulo-comodo">🍳 Cozinha</div>
            <div class="botoes">
                <a href="/cozinha/on"><button class="on">LIGAR</button></a>
                <a href="/cozinha/off"><button class="off">DESLIGAR</button></a>
            </div>
        </div>
        
        <div class="comodo">
            <div class="titulo-comodo">📺 Sala de Estar</div>
            <div class="botoes">
                <a href="/sala/on"><button class="on">LIGAR</button></a>
                <a href="/sala/off"><button class="off">DESLIGAR</button></a>
            </div>
        </div>
        
        <div class="comodo area-externa">
            <div class="titulo-comodo">🏡 Luzes Externas</div>
            <div class="botoes">
                <a href="/externa/on"><button class="on">LIGAR</button></a>
                <a href="/externa/off"><button class="off">DESLIGAR</button></a>
            </div>
        </div>
        
    </div>
</div>
</body>
</html>
"""

# ==============================================================================
# 4. SERVIDOR SOCKET HTTP (Processamento de Rotas Semânticas)
# ==============================================================================
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
server = socket.socket()
server.bind(addr)
server.listen(5)

print("Servidor HTTP rodando com sucesso...")

while True:
    try:
        client, client_addr = server.accept()
        request = client.recv(1024)
        request = str(request)
        
        # Monitoramento e Acionamento Inteligente das Novas Rotas
        if "/ar/on" in request:
            dispositivos["ar"]["pin"].value(0)
        elif "/ar/off" in request:
            dispositivos["ar"]["pin"].value(1)
            
        elif "/cozinha/on" in request:
            dispositivos["cozinha"]["pin"].value(0)
        elif "/cozinha/off" in request:
            dispositivos["cozinha"]["pin"].value(1)
            
        elif "/sala/on" in request:
            dispositivos["sala"]["pin"].value(0)
        elif "/sala/off" in request:
            dispositivos["sala"]["pin"].value(1)
            
        elif "/externa/on" in request:
            dispositivos["externa"]["pin"].value(0)
        elif "/externa/off" in request:
            dispositivos["externa"]["pin"].value(1)

        # Envio dos dados da Interface Gráfica
        response = html_dashboard()
        client.send("HTTP/1.1 200 OK\r\n")
        client.send("Content-Type: text/html\r\n")
        client.send("Connection: close\r\n\r\n")
        client.send(response)
        client.close()
        
    except Exception as e:
        print("Erro de comunicação:", e)
        
    # Proteção nativa contra travamentos rápidos do processador
    time.sleep(0.01)
