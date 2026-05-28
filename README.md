
> **Nota:** Os terminais COM, NO (Normally Open) e NC (Normally Closed) do módulo de relé conectam-se aos aparelhos de 110V/220V. **Cuidado: tensão de rede é perigosa.**

---

## 🚀 Como Instalar e Rodar

### 1. Preparando o ESP32

Certifique-se de que o seu ESP32 está rodando o firmware oficial do MicroPython. Baixe o firmware genérico para ESP32:

- **Firmware Oficial:** [micropython.org/download/ESP32_GENERIC/](https://micropython.org/download/ESP32_GENERIC/) [web:22]
- **Versão Recomendada:** `esp32-20241129-v1.24.1.bin` (nga mais recente estável)

### 2. Configurando o Projeto

Abra o arquivo `main.py` e altere as credenciais do Wi-Fi, se desejar:

```python
SSID = "FungicosESP"
PASSWORD = "SuaSenhaSeguraAbaixo"
DOMAIN_NAME = "fungicos"
```

### 3. Enviando o código para a placa

Recomenda-se o uso do utilitário `mpremote` (oficial da MicroPython). No terminal, navegue até a pasta do projeto:

```bash
# Copia o código para a raiz do ESP32
mpremote connect /dev/ttyACM0 cp main.py :main.py

# Reinicia a placa para aplicar as alterações
mpremote connect /dev/ttyACM0 reset
```

> **Nota:** Substitua `/dev/ttyACM0` pela porta serial correta:
> - **Linux:** `/dev/ttyACM0`, `/dev/ttyUSB0`
> - **Windows:** `COM3`, `COM4` (verifique no Gerenciador de Dispositivos)
> - **macOS:** `/dev/cu.usbmodem*`, `/dev/cu.usbserial*`

---

## 📱 Como Usar

1. No seu celular ou computador, abra as configurações de Wi-Fi.
2. Busque pelas redes disponíveis e conecte-se à rede `FungicosESP`.
3. Use a senha configurada (padrão: `12345678`).
4. Abra um navegador web (Chrome, Firefox, Safari, Edge).
5. Digite na barra de endereços: `http://fungicos.local` (ou `http://192.168.4.1` em Android antigos sem suporte a mDNS).
6. Use os botões no painel para ligar/desligar os aparelhos.

---

## 📜 Licença

Este projeto é de código aberto e livre para modificações. Sinta-se à vontade para clonar, alterar e adaptar para a sua própria casa. Não há garantias de nenhum tipo.

---

## 🧪 Simulação no Wokwi (Pré-Implementação)

Antes de soldar componentes, você pode simular todo o projeto no **Wokwi**, um simulador de eletrônica online gratuito e open-source.

### 🌐 Acessando o Wokwi

- **Site Oficial:** [wokwi.com](https://wokwi.com) [web:22][web:24]
- **Documentação (PT-BR):** [docs.wokwi.com/pt-BR/](https://docs.wokwi.com/pt-BR/) [web:21][web:22]
- **Template ESP32 + MicroPython:** [wokwi.com/projects/new/esp32](https://wokwi.com/projects/new/esp32)

### 📦 Componentes Equivalentes no Wokwi

| Componente Real | Componente no Wokwi | Observação |
| :--- | :--- | :--- |
| ESP32 NodeMCU-32S | `esp32` | Placa padrão, já vem com USB virtual |
| Módulo de Relé 4CH | `relay` ou `led` (substituto) | Wokwi não tem módulo de relé 4CH nativo; use 4 LEDs como feedback visual [web:31][web:32] |
| Cabo Jumper | Conexões automáticas | Arraste e conecte nos terminais |
| Fonte 5V | USB virtual do ESP32 | Alimentação embutida na simulação |

### 🔧 Configurando o diagram.json

No Wokwi, o circuito é definido no arquivo `diagram.json`. Exemplo para ESP32 + 4 LEDs (substituindo relés):

```json
{
  "version": 1,
  "author": "Miguel",
  "editor": "wokwi",
  "parts": [
    { "type": "board", "id": "esp32", "name": "ESP32", "coords": { "x": 0, "y": 0 } },
    { "type": "led", "id": "led1", "name": "LED 1 (Ar)", "coords": { "x": 100, "y": -50 } },
    { "type": "led", "id": "led2", "name": "LED 2 (Cozinha)", "coords": { "x": 100, "y": 0 } },
    { "type": "led", "id": "led3", "name": "LED 3 (Sala)", "coords": { "x": 100, "y": 50 } },
    { "type": "led", "id": "led4", "name": "LED 4 (Externa)", "coords": { "x": 100, "y": 100 } }
  ],
  "connections": [
    [ "esp32:GPIO21", "led1:A", "", "" ],
    [ "esp32:GPIO22", "led2:A", "", "" ],
    [ "esp32:GPIO13", "led3:A", "", "" ],
    [ "esp32:GPIO25", "led4:A", "", "" ],
    [ "esp32:GND", "led1:C", "", "" ],
    [ "esp32:GND", "led2:C", "", "" ],
    [ "esp32:GND", "led3:C", "", "" ],
    [ "esp32:GND", "led4:C", "", "" ]
  ]
}
```

### 🎬 Executando a Simulação

1. Acesse [wokwi.com](https://wokwi.com) e clique em **New Project → ESP32**.
2. Substitua o código em `main.py` pelo código do seu projeto.
3. Clique no botão **▶ Play** para iniciar a simulação.
4. O console serial aparece no painel inferior (se usar `print()`).
5. Para testar o servidor web, o Wokwi **não simula rede Wi-Fi AP**. Use LEDs como substituição visual do estado dos relés.

### 📚 Projetos de Referência no Wokwi

| Projeto | Link | Descrição |
| :--- | :--- | :--- |
| ESP32 + Relay + MicroPython | [wokwi.com/projects/404221238356318209](https://wokwi.com/projects/404221238356318209) [web:32] | Controle de relé simples com MicroPython |
| ESP32 + DHT22 + Relay | [wokwi.com/projects/414570544360045569](https://wokwi.com/projects/414570544360045569) [web:38] | Sensor de temperatura + controle de relé |
| ESP32 Access Point + Relay | [wokwi.com/projects/387095279849004033](https://wokwi.com/projects/387095279849004033) [web:40] | AP + controle de LED/relé |

---

## 🔧 Instalação do mpremote e esptool

Antes de enviar o código, instale as ferramentas no seu computador.

### 🐍 Instalar mpremote (todos os sistemas)

O `mpremote` é o utilitário oficial da MicroPython para controlar dispositivos remotamente.

**Pré-requisito:** Python 3.8+ instalado no seu sistema.

```bash
pip install mpremote
```

Se o comando falhar:
```bash
python -m pip install mpremote
# ou
pip3 install mpremote
```

**Verificar instalação:**
```bash
mpremote --help
```

**Documentação Oficial:** [docs.micropython.org/en/latest/reference/mpremote.html](https://docs.micropython.org/en/latest/reference/mpremote.html) [web:5][web:8]

---

### 🔌 Instalar esptool (para flash/erase)

O `esptool` é a ferramenta oficial da Espressif para apagar e gravar firmware no ESP32.

**Documentação Oficial:** [docs.espressif.com/projects/esptool](https://docs.espressif.com/projects/esptool/en/latest/esp32/) [web:17]

#### **Linux (Ubuntu/Debian/Mint/pop!_OS)**

**Opção 1: Via pip (recomendado, versão mais recente)**
```bash
pip install esptool
```

**Opção 2: Via apt + pip**
```bash
sudo apt update
sudo apt install python3-serial python3-pip
pip3 install esptool
```

**Opção 3: Via Snap**
```bash
sudo snap install espressif-esptool
sudo snap alias espressif-esptool.esptool esptool
sudo snap connect espressif-esptool:raw-usb
sudo snap connect espressif-esptool:serial
```

#### **Arch Linux / Manjaro / EndeavourOS**

**Opção 1: Via pip (recomendado)**
```bash
pip install esptool
```

**Opção 2: Via AUR (yay)**
```bash
yay -S esptool
# ou
yay -S esptool-git  # versão mais recente do git
```

**Opção 3: Pacman oficial**
```bash
sudo pacman -Sy
sudo pacman -S esptool
```

#### **Fedora**

**Opção 1: Via pip (recomendado)**
```bash
pip install esptool
```

**Opção 2: Via dnf**
```bash
sudo dnf makecache --refresh
sudo dnf -y install esptool
```

**Opção 3: Via Snap**
```bash
sudo dnf install snapd
sudo snap install espressif-esptool
```

#### **Raspberry Pi OS (Bookworm)**

```bash
python3 -m venv venv
source venv/bin/activate
pip install mpremote esptool
```

Ou com pipx:
```bash
sudo apt install pipx
pipx ensurepath
pipx install mpremote
pipx install esptool
```

#### **Windows**

**Pré-requisito:** Python 3 instalado com "Add Python to PATH" marcado.

```bash
pip install mpremote esptool
```

Se receber erro de permissão:
```bash
pip install --user mpremote esptool
```

**Verificar instalação:**
```bash
mpremote --help
esptool.py --version
```

#### **macOS**

```bash
pip3 install mpremote esptool
```

Ou via Homebrew:
```bash
brew install python
pip3 install mpremote esptool
```

---

### 🔐 Permissões no Linux (importante!)

Após instalar, adicione seu usuário ao grupo `dialout` para acessar a porta serial:

```bash
sudo usermod -a -G dialout $USER
```

**Reinicie o terminal** ou faça logout/login para aplicar as permissões.

Verifique se a porta serial está disponível:
```bash
ls -l /dev/ttyACM*  # para ESP32 conectado via USB
ls -l /dev/ttyUSB*  # para adaptadores UART
```

---

### Dica de versionamento (Git)

Dentro da pasta do seu projeto:

```bash
git init
git add main.py README.md
git commit -m "Versão final: Web server em arquivo único com Dashboard CSS Grid e mDNS"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
git push -u origin main
```

---

## ❓ Perguntas Frequentes

### 1. O que é o ESP32?

O ESP32 é um microcontrolador de baixo custo e altíssimo desempenho criado pela Espressif Systems. Ele possui Wi-Fi 802.11 b/g/n e Bluetooth 4.2 + BLE nativos embutidos no chip. Opera em 3.3V, possui dois núcleos Tensilica LX6 de 240MHz (na maioria das versões) e 52 KB de SRAM interna + 4 MB de flash externo (typical). Possui 34 pinos GPIO (General Purpose Input/Output) programáveis, SPI, I2C, I2S, ADC 12-bit, DAC 8-bit, PWM, touch sensor, e Hall sensor.

**Documentação Oficial ESP32:** [espressif.com/en/products/socs/esp32](https://www.espressif.com/en/products/socs/esp32)

### 2. Links Oficiais do MicroPython

MicroPython é uma reescrita otimizada da linguagem Python 3, projetada para rodar nas limitações de memória e processamento de microcontroladores.

| Recurso | Link |
| :--- | :--- |
| Site Oficial | [micropython.org](https://micropython.org/) [web:22] |
| Documentação Oficial | [docs.micropython.org](https://docs.micropython.org/en/latest/) [web:22] |
| Firmware ESP32 Genérico | [micropython.org/download/ESP32_GENERIC/](https://micropython.org/download/ESP32_GENERIC/) [web:22] |
| Referência GPIO MicroPython | [docs.micropython.org/en/latest/library/machine.Pin.html](https://docs.micropython.org/en/latest/library/machine.Pin.html) [web:33][web:39] |
| mpremote Documentation | [docs.micropython.org/en/latest/reference/mpremote.html](https://docs.micropython.org/en/latest/reference/mpremote.html) [web:5] |

### 3. Como Formatar (Erase) e Instalar o Firmware

Use `esptool` no Linux de terminal.

**Passo A: Apagar tudo (Erase Flash)**  
Isso destrói o sistema de arquivos corrompido e zera a placa. Se o seu ESP32 exigir o botão BOOT, segure-o enquanto roda:

```bash
esptool.py --port /dev/ttyACM0 erase_flash
```

**Passo B: Instalar o MicroPython (Write Flash)**  
Com o arquivo `.bin` na mesma pasta:

```bash
esptool.py --chip esp32 --port /dev/ttyACM0 --baud 460800 write_flash -z 0x1000 esp32-20241129-v1.24.1.bin
```

### 4. Explicação do Código: Linha a Linha

**Importações Iniciais**
```python
from machine import Pin
import network
import socket
import time
```
- `Pin`: Módulo para controlar as portas físicas do ESP32. [web:33]
- `network`: Módulo para gerenciar o Wi-Fi (criar ou conectar em redes).
- `socket`: Módulo para criar o servidor web de baixo nível (TCP/IP).
- `time`: Módulo para gerar pausas (sleep), essenciais para não travar o processador.

**Configurações e Dicionário de Dispositivos**
```python
SSID = "ESP_SANTANA"
PASSWORD = "12345678"
DOMAIN_NAME = "fungicos"

dispositivos = {
    "ar":      {"pin": Pin(21, Pin.OUT, value=1), "nome": "Ar Condicionado"},
    ...
}
```
- `SSID` e `PASSWORD`: Nome e senha da rede Wi-Fi que o ESP32 vai criar.
- `DOMAIN_NAME`: Nome para acesso via `http://fungicos.local` usando mDNS.
- `Pin(21, Pin.OUT, value=1)`: Configura o pino 21 como saída. `value=1` é crucial: módulos de relé ativos em LOW ligam quando recebem 0 (GND) e desligam quando recebem 1 (3.3V). Inicializar com 1 garante que as luzes não liguem sozinhas ao energizar. [web:33][web:39]

**Configuração do Wi-Fi (Access Point)**
```python
try:
    network.hostname(DOMAIN_NAME)
except AttributeError:
    pass

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=SSID, password=PASSWORD, authmode=network.AUTH_WPA_WPA2_PSK)

while not ap.active():
    time.sleep(0.5)
```
- `network.hostname`: Registra o nome na rede para acesso sem IP. O `try/except` evita erros em versões antigas do MicroPython.
- `network.AP_IF`: ESP32 atua como Roteador (Access Point), não como cliente (STA_IF).
- `ap.config(...)`: Define nome, senha e criptografia da rede.
- O loop `while` garante que o código só continue após a antena Wi-Fi ligar fisicamente.

**A Interface Gráfica (HTML/CSS)**
```python
def html_dashboard():
    return """<!DOCTYPE html> ... """
```
Retorna todo o código visual que o navegador vai ler. Em vez de ler de um arquivo `.html` separado (o que causaria atrasos na memória flash), entrega a string diretamente da RAM, tornando o carregamento instantâneo. O CSS possui regras responsivas (`@media`) para adaptar a "planta baixa" para telas de celular.

**O Servidor Web e o Loop Principal**
```python
addr = socket.getaddrinfo("0.0.0.0", 80)[-1]
server = socket.socket()
server.bind(addr)
server.listen(5)
```
Prepara a placa para escutar requisições na porta 80 (porta padrão HTTP). O `listen(5)` enfileira até 5 conexões simultâneas.

```python
while True:
    try:
        client, client_addr = server.accept()
        request = str(client.recv(1024))
```
- `while True`: Loop infinito principal.
- `server.accept()`: Pausa e aguarda conexão de navegador.
- `client.recv(1024)`: Lê a mensagem (clique) do celular.

```python
        if "/ar/on" in request:
            dispositivos["ar"]["pin"].value(0)
        elif "/ar/off" in request:
            dispositivos["ar"]["pin"].value(1)
```
Gatilho: Se o celular pediu `/ar/on` (Ligar Ar), envia 0 (LOW) para o pino do relé, fechando o circuito e ligando o aparelho. Se for `/ar/off`, envia 1 (HIGH), cortando energia.

```python
        response = html_dashboard()
        client.send("HTTP/1.1 200 OK\r\n")
        client.send("Content-Type: text/html\r\n")
        client.send("Connection: close\r\n\r\n")
        client.send(response)
        client.close()
```
Sempre que um botão é clicado, o ESP envia `200 OK` e entrega o HTML atualizado, encerrando a conexão (`client.close()`) para liberar memória.

```python
    except Exception as e:
        print("Erro de comunicação:", e)
        
    time.sleep(0.01)
```
- `try/except`: Evita que a placa desligue se o navegador fechar a conexão antes da hora.
- `time.sleep(0.01)`: **Linha crítica contra Watchdog Reset**. Cede 10ms de tempo livre ao processador a cada volta do loop, permitindo que ele processe regras Wi-Fi em segundo plano sem entrar em pânico.

---

## 📚 Referências Técnicas

| Tópico |Documento | Link |
| :--- | :--- | :--- |
| MicroPython ESP32 | Docs Oficiais | [docs.micropython.org/en/latest/esp32/](https://docs.micropython.org/en/latest/esp32/) [web:22] |
| GPIO MicroPython | machine.Pin | [docs.micropython.org/en/latest/library/machine.Pin.html](https://docs.micropython.org/en/latest/library/machine.Pin.html) [web:33][web:39] |
| mpremote | Docs Oficiais | [docs.micropython.org/en/latest/reference/mpremote.html](https://docs.micropython.org/en/latest/reference/mpremote.html) [web:5] |
| esptool | Docs Espressif | [docs.espressif.com/projects/esptool](https://docs.espressif.com/projects/esptool/en/latest/esp32/) [web:17] |
| Wokwi Simulator | Docs Oficiais | [docs.wokwi.com/pt-BR/](https://docs.wokwi.com/pt-BR/) [web:21][web:22] |
| ESP32 GPIO (Arduino) | API Reference | [docs.espressif.com/projects/arduino-esp32/en/latest/api/gpio.html](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/gpio.html) [web:36] |
| ESP32 GPIO Pins Guide | uPyEasy | [upesy.com/blogs/tutorials/micropython-gpio-pins-of-esp32-usage](https://www.upesy.com/blogs/tutorials/micropython-gio-pins-of-esp32-usage) [web:33] |


