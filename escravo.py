from machine import Pin
import network
import socket
import time

# ==============================================================================
# 1. CONFIGURAÇÕES GERAIS E MAPEAMENTO (Ativo em LOW)
# ==============================================================================
SSID = "ESP_SANTANA"
PASSWORD = "12345678"

# Configuração dos pinos com dicionário para manter o código limpo
dispositivos = {
    "ar":      {"pin": Pin(13, Pin.OUT, value=1), "nome": "Ar Condicionado"},
    "cozinha": {"pin": Pin(14, Pin.OUT, value=1), "nome": "Luz Cozinha"},
    "sala":    {"pin": Pin(17, Pin.OUT, value=1), "nome": "Luz Sala"},
    "externa": {"pin": Pin(18, Pin.OUT, value=1), "nome": "Luzes Externas"}
}

# ==============================================================================
# 2. CONEXÃO WI-FI COMO CLIENTE (STATION)
# ==============================================================================
sta = network.WLAN(network.STA_IF)
sta.active(True)

print(f"\nConectando na rede: {SSID}...")
sta.connect(SSID, PASSWORD)

timeout = 0
while not sta.isconnected():
    time.sleep(0.5)
    timeout += 1
    print(".", end="")
    if timeout > 30:
        print("\nFalha na conexão! Reiniciando...")
        import machine
        machine.reset()

print("\n======================================")
print(f"Conectado ao Mestre!")
print(f"IP do Escravo: {sta.ifconfig()[0]}")
print(f"Mestre: http://192.168.4.1")
print("======================================\n")

# ==============================================================================
# 3. INTERFACE WEB COM PLANTA BAIXA EM CSS GRID
# ==============================================================================
def html_dashboard():
    # Lê estado atual dos relés para mostrar no HTML
    estado_ar = "LIGADO" if dispositivos["ar"]["pin"].value() == 0 else "DESLIGADO"
    estado_cozinha = "LIGADO" if dispositivos["cozinha"]["pin"].value() == 0 else "DESLIGADO"
    estado_sala = "LIGADO" if dispositivos["sala"]["pin"].value() == 0 else "DESLIGADO"
    estado_externa = "LIGADO" if dispositivos["externa"]["pin"].value() == 0 else "DESLIGADO"
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fungicos Escravo</title>
    <style>
        :root {{
            --bg-body: #0f172a;
            --bg-blueprint: #020617;
            --bg-room: #1e293b;
            --border: #334155;
            --btn-on: #22c55e;
            --btn-off: #ef4444;
            --text-main: #f8fafc;
            --accent: #38bdf8;
            --status-on: #22c55e;
            --status-off: #ef4444;
        }}
        body {{
            background-color: var(--bg-body);
            color: var(--text-main);
            font-family: 'Segoe UI', Roboto, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
        }}
        .container {{
            width: 100%;
            max-width: 600px;
            text-align: center;
        }}
        h1 {{
            margin-bottom: 2px;
            font-size: 26px;
            color: var(--accent);
        }}
        .ip-hint {{
            color: #64748b;
            font-size: 13px;
            margin-bottom: 5px;
        }}
        .status-hint {{
            color: #22c55e;
            font-size: 12px;
            margin-bottom: 25px;
        }}
        .planta-baixa {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            background-color: var(--bg-blueprint);
            padding: 20px;
            border-radius: 24px;
            border: 3px dashed var(--border);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
        }}
        .comodo {{
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
        }}
        .comodo:hover {{
            border-color: var(--accent);
        }}
        .area-externa {{
            grid-column: span 2;
            min-height: 90px;
        }}
        .titulo-comodo {{
            font-size: 15px;
            font-weight: 600;
            color: #e2e8f0;
            margin-top: 0;
            margin-bottom: 5px;
        }}
        .estado {{
            font-size: 12px;
            margin-bottom: 10px;
            padding: 3px 10px;
            border-radius: 10px;
            background-color: #334155;
        }}
        .estado.on {{ color: var(--status-on); }}
        .estado.off {{ color: var(--status-off); }}
        .botoes {{
            display: flex;
            gap: 8px;
        }}
        button {{
            border: none;
            width: 85px;
            height: 38px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: bold;
            cursor: pointer;
            color: white;
            transition: transform 0.1s, opacity 0.2s;
        }}
        button:active {{
            transform: scale(0.95);
        }}
        .on {{ background-color: var(--btn-on); }}
        .off {{ background-color: var(--btn-off); }}
        @media (max-width: 450px) {{
            .planta-baixa {{ grid-template-columns: 1fr; }}
            .area-externa {{ grid-column: span 1; }}
        }}
    </style>
</head>
<body>
<div class="container">
    <h1>🍄 Fungicos Escravo</h1>
    <div class="ip-hint">IP: {sta.ifconfig()[0]}</div>
    <div class="status-hint">🟢 Conectado ao Mestre</div>
    
    <div class="planta-baixa">
    
        <div class="comodo">
            <div class="titulo-comodo">🛏️ Quarto (Ar Cond.)</div>
            <div class="estado {'on' if estado_ar == 'LIGADO' else 'off'}">{estado_ar}</div>
            <div class="botoes">
                <a href="/ar/on"><button class="on">LIGAR</button></a>
                <a href="/ar/off"><button class="off">DESLIGAR</button></a>
            </div>
        </div>
        
        <div class="comodo">
            <div class="titulo-comodo">🍳 Cozinha</div>
            <div class="estado {'on' if estado_cozinha == 'LIGADO' else 'off'}">{estado_cozinha}</div>
            <div class="botoes">
                <a href="/cozinha/on"><button class="on">LIGAR</button></a>
                <a href="/cozinha/off"><button class="off">DESLIGAR</button></a>
            </div>
        </div>
        
        <div class="comodo">
            <div class="titulo-comodo">📺 Sala de Estar</div>
            <div class="estado {'on' if estado_sala == 'LIGADO' else 'off'}">{estado_sala}</div>
            <div class="botoes">
                <a href="/sala/on"><button class="on">LIGAR</button></a>
                <a href="/sala/off"><button class="off">DESLIGAR</button></a>
            </div>
        </div>
        
        <div class="comodo area-externa">
            <div class="titulo-comodo">🏡 Luzes Externas</div>
            <div class="estado {'on' if estado_externa == 'LIGADO' else 'off'}">{estado_externa}</div>
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
# 4. SERVIDOR SOCKET HTTP
# ==============================================================================
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
server = socket.socket()
server.bind(addr)
server.listen(5)

print(f"Servidor HTTP rodando em http://{sta.ifconfig()[0]}")
print("Aguardando comandos do Mestre...\n")

while True:
    try:
        client, client_addr = server.accept()
        request = client.recv(1024).decode('utf-8')
        
        if request:
            primeira_linha = request.split('\r\n')[0]
            print(f"[{client_addr[0]}] {primeira_linha}")
            
            # Extrai a URL
            url = primeira_linha.split(' ')[1]
            nome = None
            estado = None
            
            # Aceita tanto /ar/on quanto /rele/ar/ON
            if '/rele/' in url:
                partes = url.split('/')
                if len(partes) >= 4:
                    nome = partes[2].lower()
                    estado = partes[3].upper()
            else:
                partes = url.split('/')
                if len(partes) >= 3:
                    nome = partes[1].lower()
                    estado = partes[2].upper()
            
            # Aciona o relé correspondente
            if nome and nome in dispositivos:
                if estado == 'ON':
                    dispositivos[nome]["pin"].value(0)
                    print(f"  -> {dispositivos[nome]['nome']}: LIGADO")
                elif estado == 'OFF':
                    dispositivos[nome]["pin"].value(1)
                    print(f"  -> {dispositivos[nome]['nome']}: DESLIGADO")

            # Envio dos dados da Interface Gráfica
            response = html_dashboard()
            client.send("HTTP/1.1 200 OK\r\n")
            client.send("Content-Type: text/html\r\n")
            client.send("Connection: close\r\n\r\n")
            client.send(response)
            client.close()
        
    except Exception as e:
        print("Erro:", e)
        
    time.sleep(0.01)
