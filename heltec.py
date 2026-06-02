from machine import Pin, SoftI2C
import ssd1306
import time

# --- 1. O SEGREDO DO HELTEC: RESET DO DISPLAY ---
# No Heltec, o pino 16 é o reset do OLED. Ele PRECISA ser ativado.
oled_reset = Pin(16, Pin.OUT)
oled_reset.value(1) 
time.sleep(0.1) # Aguarda estabilizar

# --- 2. Configuração Hardware ---
# SDA=4, SCL=15
i2c = SoftI2C(scl=Pin(15), sda=Pin(4))

try:
    oled = ssd1306.SSD1306_I2C(128, 64, i2c)
except Exception as e:
    print("Erro ao inicializar I2C:", e)

reles = {
    "ar": Pin(13, Pin.OUT, value=1),
    "cozinha": Pin(14, Pin.OUT, value=1),
    "sala": Pin(17, Pin.OUT, value=1),
    "externa": Pin(18, Pin.OUT, value=1)
}

def oled_msg(titulo, corpo):
    try:
        oled.fill(0)
        oled.text(titulo, 0, 0)
        oled.text(corpo, 0, 20)
        oled.show()
    except Exception as e:
        print("Erro no display:", e)

# --- 3. Loop de Teste Desacoplado ---
print("Iniciando sistema...")
oled_msg("SISTEMA", "Iniciando...")

while True:
    for nome, pino in reles.items():
        # A mensagem aparece no display e no terminal
        oled_msg("TESTANDO", f"Rele: {nome}")
        print(f"Testando: {nome}")
        
        # Liga (Active LOW)
        pino.value(0)
        time.sleep(1)
        
        # Desliga
        pino.value(1)
        time.sleep(0.5)
