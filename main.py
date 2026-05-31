from machine import Pin, SoftI2C, SPI, time_pulse_us
import network
import time
from umqtt.simple import MQTTClient
from mfrc522 import MFRC522
from bh1750 import BH1750

# ==============================================================================
# CONFIGURAÇÕES GERAIS
# ==============================================================================
class Config:
    WIFI_SSID = "DIRECT-NS-Santana"
    WIFI_PASSWORD = "0987654321"
    
    MQTT_CLIENT_ID = "esp32_fungicos"
    MQTT_BROKER = "192.168.49.7"  # O novo IP do seu PC na rede NetShare
    MQTT_USER = "Santana"
    MQTT_PASSWORD = "12345678"

# ==============================================================================
# CLASSES DE HARDWARE E SENSORES
# ==============================================================================
class NetworkManager:
    @staticmethod
    def connect():
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        if not sta_if.isconnected():
            print("Conectando ao Wi-Fi NetShare...")
            sta_if.connect(Config.WIFI_SSID, Config.WIFI_PASSWORD)
            while not sta_if.isconnected():
                time.sleep(0.5)
        print(f"Wi-Fi Conectado! IP: {sta_if.ifconfig()[0]}")

class RelayManager:
    def __init__(self):
        # Relés Ativos em LOW (0 = Ligado, 1 = Desligado)
        self.reles = {
            "ar": Pin(13, Pin.OUT, value=1),
            "cozinha": Pin(25, Pin.OUT, value=1),
            "sala": Pin(32, Pin.OUT, value=1),
            "externa": Pin(33, Pin.OUT, value=1)
        }

    def set_state(self, nome, estado_ligado):
        if nome in self.reles:
            self.reles[nome].value(0 if estado_ligado else 1)

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
        if duracao < 0:
            return -1
        return (duracao / 2) / 29.1


class LightSensor:
    def __init__(self, pin_scl, pin_sda):
        self.i2c = SoftI2C(scl=Pin(pin_scl), sda=Pin(pin_sda))
        # Inicializa a biblioteca BH1750 usando o barramento I2C criado
        self.sensor = BH1750(self.i2c)

    def read_lux(self):
        try:
            # Chama o método da biblioteca que você já tem
            return round(self.sensor.luminance(), 2)
        except OSError:
            return -1



class TrackerSensor:
    def __init__(self, pin_tracker):
        self.tracker = Pin(pin_tracker, Pin.IN)

    def is_detected(self):
        return self.tracker.value() == 0

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
# CONTROLADOR PRINCIPAL DO SISTEMA
# ==============================================================================
class FungosController:
    def __init__(self):
        # Estado Interno e Parâmetros Dinâmicos
        self.limite_luz = 50.0
        self.limite_distancia = 30.0
        self.estado_ventilador = False

        # Inicialização do Hardware
        self.reles = RelayManager()
        self.ultrassonico = UltrasonicSensor(27, 14)
        self.luz = LightSensor(22, 21)
        self.tracker = TrackerSensor(26)
        self.rfid = RFIDScanner(18, 23, 19, 5, 4)
        
        # Cliente MQTT
        self.mqtt = MQTTClient(Config.MQTT_CLIENT_ID, Config.MQTT_BROKER, 
                               user=Config.MQTT_USER, password=Config.MQTT_PASSWORD)
        self.mqtt.set_callback(self.mqtt_callback)

    def mqtt_callback(self, topic, msg):
        topico = topic.decode('utf-8')
        mensagem = msg.decode('utf-8')
        print(f"[{topico}] Mensagem: {mensagem}")
        
        # Parâmetros Dinâmicos
        if topico == "fungicos/config/luz":
            try:
                self.limite_luz = float(mensagem)
            except ValueError: pass
                
        elif topico == "fungicos/config/distancia":
            try:
                self.limite_distancia = float(mensagem)
            except ValueError: pass

        # Controle Manual de Relés
        elif topico.startswith("fungicos/rele/"):
            rele_nome = topico.split("/")[-1]
            ligar = (mensagem == "ON")
            self.reles.set_state(rele_nome, ligar)

    def start(self):
        NetworkManager.connect()
        
        try:
            self.mqtt.connect()
            print("Conectado ao Broker MQTT.")
            
            # Inscrições
            topicos_sub = [
                b"fungicos/rele/ar", b"fungicos/rele/cozinha", 
                b"fungicos/rele/sala", b"fungicos/rele/externa",
                b"fungicos/config/luz", b"fungicos/config/distancia"
            ]
            for t in topicos_sub:
                self.mqtt.subscribe(t)
                
        except Exception as e:
            print(f"Erro no MQTT: {e}")
            return

        self.run_loop()

    def run_loop(self):
        ultimo_envio = time.ticks_ms()
        intervalo = 2000

        while True:
            try:
                self.mqtt.check_msg()
                
                # --- LÓGICA INSTANTÂNEA: TRACKER ---
                if self.tracker.is_detected():
                    self.reles.set_state("externa", True)
                    presenca_atual = "DETECTADO"
                else:
                    self.reles.set_state("externa", False)
                    presenca_atual = "LIVRE"

                # --- LÓGICA INSTANTÂNEA: RFID ---
                uid_cartao = self.rfid.read_card()
                if uid_cartao:
                    self.mqtt.publish(b"fungicos/sensor/rfid", uid_cartao.encode())
                    self.estado_ventilador = not self.estado_ventilador
                    self.reles.set_state("ar", self.estado_ventilador)
                    time.sleep(1) # Debounce

                # --- LÓGICA COM DELAY: LUZ E DISTÂNCIA ---
                agora = time.ticks_ms()
                if time.ticks_diff(agora, ultimo_envio) > intervalo:
                    
                    self.mqtt.publish(b"fungicos/sensor/presenca", presenca_atual.encode())
                    
                    # Distância
                    dist = self.ultrassonico.read_distance()
                    if dist != -1:
                        self.mqtt.publish(b"fungicos/sensor/distancia", str(round(dist, 1)).encode())
                        self.reles.set_state("sala", dist > self.limite_distancia)
                            
                    # Luz
                    lux = self.luz.read_lux()
                    if lux != -1:
                        self.mqtt.publish(b"fungicos/sensor/luz", str(lux).encode())
                        self.reles.set_state("cozinha", lux < self.limite_luz)
                    
                    ultimo_envio = agora

                time.sleep_ms(10)
                
            except OSError as e:
                print(f"Erro no loop: {e}")
                time.sleep(5)

# ==============================================================================
# EXECUÇÃO
# ==============================================================================
if __name__ == "__main__":
    app = FungosController()
    app.start()
