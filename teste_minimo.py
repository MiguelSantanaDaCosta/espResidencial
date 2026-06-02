import network
import time

print("[1] Iniciando...")

try:
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    
    print("[2] AP ativado, configurando...")
    
    ap.config(
        essid="ESP_SANTANA",
        password="12345678",
        authmode=network.AUTH_WPA_WPA2_PSK
    )
    
    print("[3] Aguardando AP ficar ativo...")
    
    while not ap.active():
        time.sleep(0.1)
        print(".", end="")
    
    print(f"\n[4] AP ATIVO!")
    print(f"    SSID: ESP_SANTANA")
    print(f"    IP: {ap.ifconfig()[0]}")
    print(f"    Pronto! Verifique se a rede aparece no celular/PC")
    
except Exception as e:
    print(f"[ERRO]: {e}")

print("[5] Fim do script. Se não viu [4], deu erro acima.")
