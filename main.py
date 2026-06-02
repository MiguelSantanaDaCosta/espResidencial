from machine import Pin, SoftI2C, SPI, time_pulse_us
import network
import socket
import time
from umqtt.simple import MQTTClient
from mfrc522 import MFRC522
from bh1750 import BH1750
from tracker import LineTracker

# ==============================================================================
# CONFIGURAÇÕES GERAIS
# ==============================================================================
class Config:
    WIFI_SSID = "DIRECT-NS-Santana"
    WIFI_PASSWORD = "0987654321"
    
    MQTT_CLIENT_ID = "esp32_master_sensores"
    MQTT_BROKER = "192.168.49.7"
    MQTT_USER = "Santana"
    MQTT_PASSWORD = "12345678"

# ==============================================================================
# CLASSES DE HARDWARE (Sensores)
# ==============================================================================
class NetworkManager:
    @staticmethod
    def connect():
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        if not sta_if.isconnected():
            print("Conectando ao Wi-Fi...")
            sta_if.connect(Config.WIFI_SSID, Config.WIFI_PASSWORD)
            while not sta_if.isconnected():
                time.sleep(0.5)
        ip = sta_if.ifconfig()[0]
        print(f"Wi-Fi Conectado! Acesse o painel em: http://{ip}")
        return ip

class UltrasonicSensor:
    def __init__(self, pin_trigger, pin_echo):
        self.trigger = Pin(pin_trigger, Pin.OUT)
        self.echo = Pin(pin_echo, Pin.IN)

    def read_distance(self):
        self.trigger.value(0)
        time.sleep_us(2)
        self.trigger.value(1)
        time.sleep_us(10)
        self.trigger.value(0)
        duracao = time_pulse_us(self.echo, 1, 30000)
        return (duracao / 2) / 29.1 if duracao > 0 else -1

class LightSensor:
    def __init__(self, pin_scl, pin_sda):
        self.i2c = SoftI2C(scl=Pin(pin_scl), sda=Pin(pin_sda))
        self.sensor = BH1750(self.i2c)

    def read_lux(self):
        try:
            return round(self.sensor.luminance(), 2)
        except:
            return -1

class RFIDScanner:
    def __init__(self, sck, mosi, miso, cs, rst):
        self.spi = SPI(2, baudrate=2500000, polarity=0, phase=0, 
                       sck=Pin(sck), mosi=Pin(mosi), miso=Pin(miso))
        self.rfid = MFRC522(self.spi, cs=Pin(cs), rst=Pin(rst))

    def read_card(self):
        (status, tag_type) = self.rfid.request(self.rfid.REQIDL)
        if status == self.rfid.OK:
            (status, uid) = self.rfid.anticoll()
            if status == self.rfid.OK:
                return "0x%02x%02x%02x%02x" % (uid[0], uid[1], uid[2], uid[3])
        return None

# ==============================================================================
# CONTROLADOR MESTRE E SERVIDOR WEB
# ==============================================================================
class FungosMaster:
    def __init__(self):
        # Estados e Limites
        self.limites = {"luz": 50.0, "distancia": 30.0}
        self.leituras = {"luz": 0, "distancia": 0, "presenca": "LIVRE", "rfid": "Aguardando..."}
        
        # Status real reportado pelo Heltec
        self.reles = {"ar": "OFF", "cozinha": "OFF", "sala": "OFF", "externa": "OFF"}
        # Controle de repetição para não floodar o MQTT
        self.estado_enviado = {"ar": "", "cozinha": "", "sala": "", "externa": ""}
        
        self.estado_ventilador = False

        # Sensores
        self.ultrassonico = UltrasonicSensor(27, 14)
        self.luz = LightSensor(22, 21)
        self.tracker = LineTracker(26, pin_type=Pin.IN, use_pull=True)
        self.rfid = RFIDScanner(18, 23, 19, 5, 4)
        
        # MQTT e WebServer
        self.mqtt = MQTTClient(Config.MQTT_CLIENT_ID, Config.MQTT_BROKER, 
                               user=Config.MQTT_USER, password=Config.MQTT_PASSWORD)
        self.server = None

    def setup_webserver(self):
        addr = socket.getaddrinfo("0.0.0.0", 80)[-1]
        self.server = socket.socket()
        self.server.bind(addr)
        self.server.listen(5)
        self.server.setblocking(False) # Muito importante para não travar o loop de sensores
        print("Servidor Web iniciado.")

    def mqtt_callback(self, topic, msg):
        topico = topic.decode('utf-8')
        mensagem = msg.decode('utf-8')
        
        # Recebe o status real do Heltec para atualizar a interface gráfica
        if topico.startswith("fungicos/rele/status/"):
            rele_nome = topico.split("/")[-1]
            if rele_nome in self.reles:
                self.reles[rele_nome] = mensagem
                self.estado_enviado[rele_nome] = mensagem

    def publicar_comando_rele(self, nome, estado):
        # Só publica se o estado mudou, evita spam no broker MQTT
        if self.estado_enviado[nome] != estado:
            self.mqtt.publish(f"fungicos/rele/comando/{nome}".encode(), estado.encode())
            self.estado_enviado[nome] = estado
            print(f"Comando Enviado: {nome} -> {estado}")

    def gerar_html(self):
        html = """<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; background-color: #121212; color: #ffffff; text-align: center; margin: 0; padding: 20px; }
            .card { background: #1e1e1e; padding: 20px; margin: 10px auto; border-radius: 10px; max-width: 400px; box-shadow: 0 4px 8px rgba(0,0,0,0.5); }
            .btn { display: inline-block; padding: 10px 20px; margin: 5px; text-decoration: none; border-radius: 5px; font-weight: bold; color: white; }
            .btn-on { background-color: #4CAF50; } .btn-off { background-color: #F44336; }
            .input-group { margin: 10px 0; } input { width: 60px; padding: 5px; text-align: center; }
        </style>
        <title>Painel Fungicos</title>
        </head><body>
        <h1>🍄 Cultivo Controlado</h1>
        
        <div class="card">
            <h3>📊 Sensores em Tempo Real</h3>
            <p>Luminosidade: <b>{luz} Lux</b></p>
            <p>Distância: <b>{dist} cm</b></p>
            <p>Movimento (IR): <b>{presenca}</b></p>
            <p>Último Cartão: <b>{rfid}</b></p>
            <a href="/" class="btn" style="background-color: #2196F3;">Atualizar Dados</a>
        </div>

        <div class="card">
            <h3>⚙️ Configuração Automática</h3>
            <form action="/config" method="GET">
                <div class="input-group">
                    <label>Luz Alvo (Lux):</label>
                    <input type="number" step="0.1" name="luz" value="{lim_luz}">
                </div>
                <div class="input-group">
                    <label>Distância Alvo (cm):</label>
                    <input type="number" step="0.1" name="dist" value="{lim_dist}">
                </div>
                <button type="submit" class="btn" style="background-color: #FF9800;">Salvar Limites</button>
            </form>
        </div>

        <div class="card">
            <h3>🔌 Controle Manual de Relés</h3>
            """
        
        # Preenche os botões de relés
        for nome, status in self.reles.items():
            html += f"<p>{nome.upper()}: <b>{status}</b><br>"
            html += f"<a href='/rele/{nome}/on' class='btn btn-on'>LIGAR</a>"
            html += f"<a href='/rele/{nome}/off' class='btn btn-off'>DESLIGAR</a></p>"
            
        html += "</div></body></html>"
        
        return html.format(
            luz=self.leituras["luz"], dist=self.leituras["distancia"], 
            presenca=self.leituras["presenca"], rfid=self.leituras["rfid"],
            lim_luz=self.limites["luz"], lim_dist=self.limites["distancia"]
        )

    def processar_servidor_web(self):
        try:
            client, addr = self.server.accept()
            client.settimeout(0.5)
            request = client.recv(1024).decode('utf-8')
            
            if request:
                primeira_linha = request.split('\r\n')[0]
                url = primeira_linha.split(' ')[1]

                # Rota: Controle Manual (/rele/ar/on)
                if url.startswith('/rele/'):
                    partes = url.split('/')
                    if len(partes) >= 4:
                        rele = partes[2]
                        acao = partes[3].upper() # ON ou OFF
                        self.publicar_comando_rele(rele, acao)
                
                # Rota: Alterar Limites (/config?luz=50&dist=30)
                elif url.startswith('/config?'):
                    parametros = url.split('?')[1].split('&')
                    for p in parametros:
                        chave, valor = p.split('=')
                        if chave in self.limites:
                            self.limites[chave] = float(valor)

            # Responde sempre com a página principal atualizada
            resposta = self.gerar_html()
            client.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n")
            client.send(resposta)
            client.close()
            
        except OSError:
            pass # Nenhuma conexão recebida, segue o loop

    def start(self):
        NetworkManager.connect()
        self.setup_webserver()
        
        try:
            self.mqtt.set_callback(self.mqtt_callback)
            self.mqtt.connect()
            self.mqtt.subscribe(b"fungicos/rele/status/#")
            print("Conectado ao MQTT. Escutando status dos relés...")
        except Exception as e:
            print(f"Erro no MQTT: {e}")
            return

        self.run_loop()

    def run_loop(self):
        ultimo_envio = time.ticks_ms()

        while True:
            # 1. Processa Rede e Dashboard Web (Não bloqueante)
            self.mqtt.check_msg()
            self.processar_servidor_web()
            
            # 2. Leitura Instantânea: Tracker IR
            if self.tracker.is_line_present():
                self.leituras["presenca"] = "DETECTADO"
                self.publicar_comando_rele("externa", "ON")
            else:
                self.leituras["presenca"] = "LIVRE"
                self.publicar_comando_rele("externa", "OFF")

            # 3. Leitura Instantânea: RFID
            uid = self.rfid.read_card()
            if uid:
                self.leituras["rfid"] = uid
                self.mqtt.publish(b"fungicos/sensor/rfid", uid.encode())
                # Toggle do ventilador (Alterna o estado atual)
                self.estado_ventilador = not self.estado_ventilador
                novo_estado = "ON" if self.estado_ventilador else "OFF"
                self.publicar_comando_rele("ar", novo_estado)
                time.sleep(1) # Debounce para não ler o cartão 50 vezes num segundo

            # 4. Leituras Periódicas (Luz e Distância) a cada 2 segundos
            if time.ticks_diff(time.ticks_ms(), ultimo_envio) > 2000:
                self.mqtt.publish(b"fungicos/sensor/presenca", self.leituras["presenca"].encode())
                
                # --- Ultrassônico ---
                dist = self.ultrassonico.read_distance()
                if dist != -1:
                    dist_arredondada = round(dist, 1)
                    self.leituras["distancia"] = dist_arredondada
                    self.mqtt.publish(b"fungicos/sensor/distancia", str(dist_arredondada).encode())
                    
                    # Lógica com Histerese (Evita o "click-click" irritante)
                    if dist > (self.limites["distancia"] + 2):
                        self.publicar_comando_rele("sala", "ON")
                    elif dist < (self.limites["distancia"] - 2):
                        self.publicar_comando_rele("sala", "OFF")
                        
                # --- Luminosidade ---
                lux = self.luz.read_lux()
                if lux != -1:
                    self.leituras["luz"] = lux
                    self.mqtt.publish(b"fungicos/sensor/luz", str(lux).encode())
                    
                    if lux < (self.limites["luz"] - 5):
                        self.publicar_comando_rele("cozinha", "ON")
                    elif lux > (self.limites["luz"] + 5):
                        self.publicar_comando_rele("cozinha", "OFF")
                
                ultimo_envio = time.ticks_ms()

            time.sleep_ms(20) # Alívio para o processador (Watchdog)

if __name__ == "__main__":
    app = FungosMaster()
    app.start()
