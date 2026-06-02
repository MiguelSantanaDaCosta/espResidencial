from machine import Pin, SoftI2C
import network
import socket
import time
import ssd1306

# ==============================================================================
# CONFIGURAÇÃO WIFI (AP DO ESP MESTRE)
# ===================================================================================================================================


# ==============================================================================
# CONEXÃO WIFI (CONFIGURAÇÃO PARA CLIENTE DO MESTRE)
# ==============================================================================
SSID = "ESP_SANTANA"      # Nome da rede criada pelo Mestre
PASSWORD = "12345678"

display_boot("Conectando", "AO MESTRE")

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

# FORÇA IP ESTÁTICO (IMPORTANTE!)
# IP do Escravo: 192.168.4.2
# Gateway/DNS: 192.168.4.1 (IP padrão do Mestre como AP)
sta_if.ifconfig(('192.168.4.2', '255.255.255.0', '192.168.4.1', '192.168.4.1'))

if not sta_if.isconnected():
    sta_if.connect(SSID, PASSWORD)
    while not sta_if.isconnected():
        print("Conectando ao Mestre...")
        time.sleep(1)

print("Conectado! IP:", sta_if.ifconfig()[0])
display_boot("WiFi OK", "192.168.4.2")
time.sleep(2)
# RELÉS (ATIVOS EM LOW)
# ==============================================================================
dispositivos = {
    "ar":      {"pin": Pin(13, Pin.OUT, value=1)},
    "cozinha": {"pin": Pin(14, Pin.OUT, value=1)},
    "sala":    {"pin": Pin(17, Pin.OUT, value=1)},
    "externa": {"pin": Pin(18, Pin.OUT, value=1)}
}

# ==============================================================================
# OLED HELTEC
# ==============================================================================
oled_reset = Pin(16, Pin.OUT)
oled_reset.value(1)
time.sleep(0.1)

i2c = SoftI2C(
    scl=Pin(15),
    sda=Pin(4)
)

try:
    oled = ssd1306.SSD1306_I2C(
        128,
        64,
        i2c
    )
except Exception as e:
    print("Erro OLED:", e)
    oled = None

# ==============================================================================
# DISPLAY
# ==============================================================================
def display_boot(titulo, status):

    if not oled:
        return

    oled.fill(0)

    oled.text("== HELTEC ==", 10, 0)
    oled.text(titulo, 0, 20)
    oled.text(status, 0, 35)

    oled.show()

def estado_rele(nome):

    return (
        "ON"
        if dispositivos[nome]["pin"].value() == 0
        else "OFF"
    )

def update_dashboard(ultimo="Aguardando"):

    if not oled:
        return

    oled.fill(0)

    ip = (
        sta_if.ifconfig()[0]
        if sta_if.isconnected()
        else "Offline"
    )

    oled.text("IP:", 0, 0)
    oled.text(ip, 0, 10)

    oled.hline(0, 20, 128, 1)

    oled.text(
        "AR:" + estado_rele("ar"),
        0,
        24
    )

    oled.text(
        "CZ:" + estado_rele("cozinha"),
        64,
        24
    )

    oled.text(
        "SL:" + estado_rele("sala"),
        0,
        36
    )

    oled.text(
        "EX:" + estado_rele("externa"),
        64,
        36
    )

    oled.hline(0, 48, 128, 1)

    oled.text("CMD:", 0, 52)

    if len(ultimo) > 12:
        ultimo = ultimo[:12]

    oled.text(ultimo, 40, 52)

    oled.show()

# ==============================================================================
# CONTROLE DOS RELÉS
# ==============================================================================
def controlar_rele(nome, estado):

    if nome not in dispositivos:
        return False

    try:

        if estado.lower() == "on":

            # Relé ativo em LOW
            dispositivos[nome]["pin"].value(0)

        else:

            dispositivos[nome]["pin"].value(1)

        update_dashboard(
            "{} {}".format(
                nome.upper(),
                estado.upper()
            )
        )

        print(
            "[RELE]",
            nome,
            estado
        )

        return True

    except Exception as e:

        print(e)

        return False

# ==============================================================================
# CONEXÃO WIFI
# ==============================================================================
display_boot(
    "Conectando",
    SSID
)

sta_if = network.WLAN(network.STA_IF)

sta_if.active(True)

if not sta_if.isconnected():

    sta_if.connect(
        SSID,
        PASSWORD
    )

    while not sta_if.isconnected():

        print("Conectando...")

        time.sleep(1)

ip = sta_if.ifconfig()[0]

print("WiFi conectado")
print("IP:", ip)

display_boot(
    "WiFi OK",
    ip
)

time.sleep(2)

# ==============================================================================
# SERVIDOR HTTP
# ==============================================================================
addr = socket.getaddrinfo(
    "0.0.0.0",
    80
)[0][-1]

server = socket.socket()

server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server.bind(addr)

server.listen(5)

print("Servidor iniciado")

update_dashboard("Pronto")

# ==============================================================================
# LOOP PRINCIPAL
# ==============================================================================
while True:

    try:

        client, endereco = server.accept()

        request = client.recv(
            1024
        ).decode()

        if request:

            primeira_linha = request.split(
                "\r\n"
            )[0]

            print(
                "[HTTP]",
                primeira_linha
            )

            try:

                rota = primeira_linha.split(
                    " "
                )[1]

            except:

                rota = "/"

            # --------------------------------------------------
            # /rele/ar/on
            # /rele/ar/off
            # --------------------------------------------------

            if rota.startswith("/rele/"):

                partes = rota.split("/")

                if len(partes) >= 4:

                    rele = partes[2]

                    estado = partes[3]

                    controlar_rele(
                        rele,
                        estado
                    )

            # --------------------------------------------------
            # STATUS JSON
            # --------------------------------------------------

            elif rota == "/status":

                json_status = """
{
 "ar":"%s",
 "cozinha":"%s",
 "sala":"%s",
 "externa":"%s"
}
""" % (
                    estado_rele("ar"),
                    estado_rele("cozinha"),
                    estado_rele("sala"),
                    estado_rele("externa")
                )

                client.send(
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: application/json\r\n"
                    "Connection: close\r\n\r\n"
                )

                client.send(
                    json_status
                )

                client.close()

                continue

            client.send(
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                "Connection: close\r\n\r\nOK"
            )

        client.close()

    except Exception as e:

        print(
            "Erro:",
            e
        )

        try:
            client.close()
        except:
            pass

    time.sleep_ms(50)
