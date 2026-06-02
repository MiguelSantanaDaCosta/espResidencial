# ==============================================================================
# MAPEAMENTO DE PINAGEM DO SINAL (GPIO - ESP32)
# ==============================================================================
import machine
from machine import Pin, I2C, SPI, time_pulse_us
import network
import socket
import time
import json
from umqtt.simple import MQTTClient
from mfrc522 import MFRC522
from bh1750 import BH1750
from aht21 import AHT21
import ens160
from tracker import LineTracker

# ==============================================================================
# CONFIGURAÇÕES GERAIS
# ==============================================================================
class Config:
    WIFI_SSID = "Roteador"
    WIFI_PASSWORD = "12345678"

    MQTT_CLIENT_ID = "esp32_master_sensores"
    MQTT_BROKER = "10.77.236.7"
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
            print("[Wi-Fi] Conectando...")
            sta_if.connect(Config.WIFI_SSID, Config.WIFI_PASSWORD)
            while not sta_if.isconnected():
                time.sleep(0.5)
        ip = sta_if.ifconfig()[0]
        print(f"[Wi-Fi] Conectado! Painel: http://{ip}")
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
    def __init__(self, i2c_bus):
        try:
            self.sensor = BH1750(i2c_bus)
            print("[BH1750] Sensor de luz iniciado.")
        except Exception as e:
            print("[BH1750] Erro:", e)
            self.sensor = None

    def read_lux(self):
        if not self.sensor:
            return -1
        try:
            return round(self.sensor.luminance(), 2)
        except Exception as e:
            print("[BH1750] Erro leitura:", e)
            return -1

class AirClimateSensor:
    def __init__(self, i2c_bus):
        self.climate = None
        self.air = None
        try:
            self.climate = AHT21(i2c_bus)
            print("[AHT21] Sensor de clima iniciado.")
        except Exception as e:
            print("[AHT21] Erro:", e)
        try:
            self.air = ens160.ENS160(i2c_bus)
            print("[ENS160] Sensor de ar iniciado.")
        except Exception as e:
            print("[ENS160] Erro:", e)

    def read_all(self):
        temp, hum, eco2, tvoc, aqi = None, None, None, None, None
        
        if self.climate:
            try:
                temp, hum = self.climate.measure()
                temp = round(temp, 1)
                hum = round(hum, 1)
            except Exception as e:
                print("[AHT21] Erro leitura:", e)
        
        if self.air:
            try:
                air_data = self.air.get_data()
                eco2 = air_data["eCO2"]
                tvoc = air_data["TVOC"]
                aqi = air_data["AQI"]
            except Exception as e:
                print("[ENS160] Erro leitura:", e)
        
        return temp, hum, eco2, tvoc, aqi

class RFIDScanner:
    def __init__(self, sck, mosi, miso, cs, rst):
        try:
            self.spi = SPI(2, baudrate=2500000, polarity=0, phase=0,
                           sck=Pin(sck), mosi=Pin(mosi), miso=Pin(miso))
            self.rfid = MFRC522(sck=sck, mosi=mosi, miso=miso, rst=rst, cs=cs)
            print("[RFID] Leitor RFID iniciado com sucesso.")
        except Exception as e:
            print("[RFID] Erro ao iniciar:", e)
            self.rfid = None

    def read_card(self):
        if not self.rfid:
            return None
        try:
            (status, uid) = self.rfid.SelectTagSN()
            if status == self.rfid.OK:
                uid_str = "0x" + "".join(["{:02x}".format(i) for i in uid])
                agora = time.localtime()
                horario = f"{agora[3]:02d}:{agora[4]:02d}:{agora[5]:02d}"
                print(f"[RFID] Tag detectada: {uid_str} ({horario})")
                return f"{uid_str} ({horario})"
        except Exception as e:
            print("[RFID] Erro leitura:", e)
        return None

# ==============================================================================
# CONTROLADOR MESTRE E SERVIDOR WEB
# ==============================================================================
class FungosMaster:
    def __init__(self):
        self.limites = {"luz": 50.0, "distancia": 5.0}
        self.leituras = {
            "luz": 0, "distancia": 0, "presenca": "LIVRE", "presenca_ultra": "LIVRE",
            "rfid": "Aguardando...",
            "temp": 0, "hum": 0, "co2": 0, "tvoc": 0, "aqi": 0
        }

        self.reles = {"ar": "OFF", "cozinha": "OFF", "sala": "OFF", "externa": "OFF"}
        self.estado_enviado = {"ar": "", "cozinha": "", "sala": "", "externa": ""}
        self.estado_ventilador = False

        # Inicializa I2C e verifica dispositivos
        self.i2c_bus = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)
        print("[I2C] Dispositivos detectados:", [hex(d) for d in self.i2c_bus.scan()])

        self.ultrassonico = UltrasonicSensor(27, 14)
        self.luz = LightSensor(self.i2c_bus)
        self.clima_ar = AirClimateSensor(self.i2c_bus)
        self.tracker = LineTracker(26, pin_type=Pin.IN, use_pull=True)
        self.rfid = RFIDScanner(18, 23, 19, 5, 4)

        self.mqtt = None
        self.server = None

    def setup_ap(self):
        self.SSID = "ESP_SANTANA"
        self.PASSWORD = "12345678"
        self.DOMAIN_NAME = "fungicos"

        try:
            network.hostname(self.DOMAIN_NAME)
        except AttributeError:
            pass

        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(True)
        self.ap.config(
            essid=self.SSID,
            password=self.PASSWORD,
            authmode=network.AUTH_WPA_WPA2_PSK
        )

        while not self.ap.active():
            time.sleep(0.1)

        print(f"[AP] Rede '{self.SSID}' iniciada com sucesso.")
        print(f"[AP] IP do Mestre: {self.ap.ifconfig()[0]}")

    def enviar_comando_http(self, rele, estado):
        """Envia comando direto via Socket HTTP para o IP fixo do escravo"""
        try:
            addr = socket.getaddrinfo("192.168.4.2", 80)[0][-1]
            s = socket.socket()
            s.settimeout(0.5)
            s.connect(addr)
            msg = f"GET /rele/{rele}/{estado} HTTP/1.1\r\nHost: 192.168.4.2\r\n\r\n"
            s.send(msg.encode())
            s.close()
            print(f"[HTTP] Comando {rele} -> {estado} enviado ao Escravo.")
        except Exception as e:
            print(f"[Erro] Falha ao comunicar com Escravo: {e}")

    def setup_webserver(self):
        addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
        self.server = socket.socket()
        self.server.bind(addr)
        self.server.listen(5)
        self.server.setblocking(False)
        print("[Web] Servidor iniciado.")

    def publicar_comando_rele(self, nome, estado):
        if self.mqtt and self.estado_enviado.get(nome) != estado:
            try:
                topico = f"fungicos/rele/comando/{nome}"
                self.mqtt.publish(topico.encode(), estado.encode())
                self.estado_enviado[nome] = estado
                print(f"[MQTT] {nome} -> {estado}")
            except Exception as e:
                print("Erro ao publicar MQTT:", e)

    def gerar_html(self):
        html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Fungicos</title>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #121212; color: #ffffff; text-align: center; margin: 0; padding: 10px; }}
        .grid {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; }}
        .card {{ background: #1e1e1e; padding: 20px; border-radius: 10px; width: 100%; max-width: 350px; box-shadow: 0 4px 8px rgba(0,0,0,0.5); }}
        .btn {{ display: inline-block; padding: 10px 20px; margin: 5px; text-decoration: none; border-radius: 5px; font-weight: bold; color: white; cursor: pointer; border: none; }}
        .btn-on {{ background-color: #4CAF50; }} .btn-off {{ background-color: #F44336; }}
        .input-group {{ margin: 10px 0; }} input {{ width: 60px; padding: 5px; text-align: center; }}
        .sensor-data p {{ margin: 8px 0; font-size: 15px; border-bottom: 1px solid #333; padding-bottom: 5px; }}
        .sensor-data b {{ color: #4CAF50; }}
        .alerta {{ color: #ff9800; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>🍄 Cultivo Controlado</h1>
    <div class="grid">
        <div class="card sensor-data">
            <h3>📊 Sensores de Ambiente</h3>
            <p>Temperatura: <b>{temp} °C</b></p>
            <p>Umidade: <b>{hum} %</b></p>
            <p>eCO2: <b>{co2} ppm</b></p>
            <p>TVOC: <b>{tvoc} ppb</b></p>
            <p>AQI: <b>{aqi}</b></p>
            <p>Luminosidade: <b>{luz} Lux</b></p>
        </div>
        <div class="card sensor-data">
            <h3>🛡️ Segurança e Presença</h3>
            <p>Distância: <b>{dist} cm</b></p>
            <p>Movimento (IR): <b>{presenca}</b></p>
            <p>Presença (Ultra): <b class="alerta">{presenca_ultra}</b></p>
            <p style="border:none;">Acesso RFID:<br> <b style="color:#2196F3; font-size:14px;">{rfid}</b></p>
        </div>
        <div class="card">
            <h3>🔌 Controle Manual de Relés</h3>
            <div id="reles-container">
        """
        for nome, status in self.reles.items():
            html += f"<p style='margin-top:15px; margin-bottom:5px;'>{nome.upper()}: <b>{status}</b></p>"
            html += f"<button class='btn btn-on' onclick=\"fetch('/rele/{nome}/on')\">LIGAR</button>"
            html += f"<button class='btn btn-off' onclick=\"fetch('/rele/{nome}/off')\">DESLIGAR</button>"

        html += """
            </div>
        </div>
        <div class="card">
            <h3>⚙️ Configuração Automática</h3>
            <form action="/config" method="GET">
                <div class="input-group"><label>Luz Alvo (Lux):</label> <input type="number" step="0.1" name="luz" value="{lim_luz}"></div>
                <div class="input-group"><label>Distância Alvo (cm):</label> <input type="number" step="0.1" name="dist" value="{lim_dist}"></div>
                <button type="submit" class="btn" style="background-color: #FF9800; width: 100%;">Salvar Limites</button>
            </form>
        </div>
    </div>
    <script>
        setInterval(() => {{
            fetch('/api/data')
                .then(res => res.json())
                .then(data => {{ location.reload(); }}).catch(() => {{}});
        }}, 3000);
    </script>
</body>
</html>
"""
        return html.format(
            luz=self.leituras["luz"], dist=self.leituras["distancia"],
            presenca=self.leituras["presenca"], presenca_ultra=self.leituras["presenca_ultra"],
            rfid=self.leituras["rfid"],
            temp=self.leituras["temp"], hum=self.leituras["hum"],
            co2=self.leituras["co2"], tvoc=self.leituras["tvoc"], aqi=self.leituras["aqi"],
            lim_luz=self.limites["luz"], lim_dist=self.limites["distancia"]
        )

    def processar_servidor_web(self):
        try:
            self.server.settimeout(0.05)
            client, addr = self.server.accept()
            client.settimeout(0.5)
            request = client.recv(1024).decode('utf-8')

            if request:
                primeira_linha = request.split('\r\n')[0]
                url = primeira_linha.split(' ')[1]

                if url.startswith('/api/data'):
                    client.send("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n")
                    client.send(json.dumps(self.leituras))
                    client.close()
                    return

                elif url.startswith('/rele/'):
                    partes = url.split('/')
                    if len(partes) >= 4:
                        rele = partes[2]
                        acao = partes[3].upper()
                        self.publicar_comando_rele(rele, acao)
                        self.enviar_comando_http(rele, acao)
                        client.send("HTTP/1.1 200 OK\r\nConnection: close\r\n\r\nOK")
                        client.close()
                        return

                elif url.startswith('/config?'):
                    parametros = url.split('?')[1].split('&')
                    for p in parametros:
                        chave, valor = p.split('=')
                        if chave in self.limites:
                            self.limites[chave] = float(valor)

            resposta = self.gerar_html()
            client.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n")
            client.send(resposta)
            client.close()

        except OSError:
            pass

    def start(self):
        self.setup_ap()
        self.setup_webserver()

        try:
            self.mqtt = MQTTClient(
                Config.MQTT_CLIENT_ID,
                Config.MQTT_BROKER,
                user=Config.MQTT_USER,
                password=Config.MQTT_PASSWORD
            )
            self.mqtt.connect()
            self.mqtt.subscribe(b"fungicos/rele/status/#")
            print("[MQTT] Conectado com sucesso.")
        except Exception as e:
            print("[MQTT] Indisponivel, operando sem MQTT:", e)
            self.mqtt = None

        self.run_loop()

    def run_loop(self):
        ultimo_envio = time.ticks_ms()
        contador = 0

        while True:
            # Atende requisicoes web com mais frequencia
            self.processar_servidor_web()
            self.processar_servidor_web()
            self.processar_servidor_web()
            self.processar_servidor_web()
            self.processar_servidor_web()

            contador += 1

            # Sensor IR (presenca)
            try:
                if self.tracker.is_line_present():
                    self.leituras["presenca"] = "DETECTADO"
                    self.enviar_comando_http("externa", "ON")
                else:
                    self.leituras["presenca"] = "LIVRE"
                    self.enviar_comando_http("externa", "OFF")
            except:
                pass

            # RFID a cada 5 iteracoes
            if contador % 5 == 0:
                try:
                    uid = self.rfid.read_card()
                    if uid:
                        self.leituras["rfid"] = uid
                        self.estado_ventilador = not self.estado_ventilador
                        novo_estado = "ON" if self.estado_ventilador else "OFF"
                        self.enviar_comando_http("ar", novo_estado)
                except:
                    pass

            # Sensores lentos a cada 3 segundos
            if time.ticks_diff(time.ticks_ms(), ultimo_envio) > 3000:
                # Ultrassonico - aciona quando MENOS de 5cm
                try:
                    dist = self.ultrassonico.read_distance()
                    if dist != -1:
                        self.leituras["distancia"] = round(dist, 1)
                        # Se distancia menor que 5cm, alguem esta muito proximo
                        if 0 < dist < 5:
                            self.leituras["presenca_ultra"] = "DETECTADO"
                            self.enviar_comando_http("sala", "ON")
                            print(f"[ULTRA] Presenca detectada a {dist:.1f}cm - Acionando Sala")
                        else:
                            self.leituras["presenca_ultra"] = "LIVRE"
                            self.enviar_comando_http("sala", "OFF")
                except Exception as e:
                    print("[ULTRA] Erro:", e)

                # Luminosidade
                try:
                    lux = self.luz.read_lux()
                    if lux != -1:
                        self.leituras["luz"] = lux
                        if lux < (self.limites["luz"] - 5):
                            self.enviar_comando_http("cozinha", "ON")
                        elif lux > (self.limites["luz"] + 5):
                            self.enviar_comando_http("cozinha", "OFF")
                except:
                    pass

                # Clima e Ar
                try:
                    temp, hum, eco2, tvoc, aqi = self.clima_ar.read_all()
                    if temp is not None:
                        self.leituras.update({"temp": temp, "hum": hum, "co2": eco2, "tvoc": tvoc, "aqi": aqi})
                except:
                    pass

                ultimo_envio = time.ticks_ms()

            time.sleep_ms(10)

if __name__ == "__main__":
    app = FungosMaster()
    app.start()
