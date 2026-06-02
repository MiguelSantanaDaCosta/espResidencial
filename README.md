
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

## 📝 Como usar no Wokwi

### 1. Criar novo projeto
Acesse: [https://wokwi.com/projects/new/esp32](https://wokwi.com/projects/new/esp32). [web:50]

### 2. Substituir arquivos
- `diagram.json ou wokwi.json` → cole o JSON acima.
- `main.py` → cole o código `esp.py` do **MESTRE**.
- Adicione as bibliotecas como arquivos `.py` no projeto. [web:48][web:51]

### 3. Adicionar bibliotecas
No painel esquerdo, adicione os arquivos:

- `bh1750.py`
- `aht21.py`
- `ens160.py`
- `mfrc522.py`
- `tracker.py`
- `simple.py`
- `urequests.py` [web:48][web:51]

### 4. Simular
Clique em **Start Simulation** para iniciar a execução. [web:50]

---

## 🎮 Controles interativos

| Sensor | Como simular |
|---|---|
| HC-SR04 | Clique no sensor e arraste o slider de distância. [web:49] |
| BH1750 | Clique e ajuste o valor de luminosidade. |
| AHT21 | Clique e altere temperatura e umidade. |
| IR Tracker | Clique para alternar entre HIGH e LOW. |
| Relés | Clique nos botões do escravo para ligar e desligar. |

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

# Fungicos - Sistema de Automação Residencial

## Visão geral do projeto

Sistema de automação para cultivo controlado de fungos, composto por 2 ESP32 (Mestre e Escravo) integrados com Node-RED para monitoramento e controle via dashboard web.

---

## Arquitetura do sistema

```text
┌─────────────────────────────────────────────────────────────┐
│                    REDE WiFi ESP_SANTANA                     │
│                       192.168.4.0/24                         │
│                                                              │
│  ┌─────────────────────┐       ┌─────────────────────────┐  │
│  │   🔵 ESP32 MESTRE    │       │    🟢 ESP32 ESCRAVO      │  │
│  │   192.168.4.1        │       │    192.168.4.2           │  │
│  │                      │ HTTP  │                          │  │
│  │  📡 Sensores:        │──────▶│  🔌 Relés:               │  │
│  │  -  HC-SR04 (Dist)   │       │  -  Ar Condicionado       │  │
│  │  -  BH1750 (Luz)     │       │  -  Luz Cozinha           │  │
│  │  -  AHT21 (Temp/Hum) │       │  -  Luz Sala              │  │
│  │  -  ENS160 (Ar)      │       │  -  Luzes Externas        │  │
│  │  -  MFRC522 (RFID)   │       │                          │  │
│  │  -  Tracker IR       │       │  🌐 Servidor Web:        │  │
│  │                      │       │  Planta Baixa Interativa │  │
│  │  🌐 Servidor Web:    │       │                          │  │
│  │  Painel de Sensores  │       │                          │  │
│  └─────────────────────┘       └─────────────────────────┘  │
│           │                              │                   │
│           │         (futuro)             │                   │
│           └──────────┬──────────────────┘                   │
│                      │                                      │
└──────────────────────┼──────────────────────────────────────┘
                       │
              ┌────────▼─────────┐
              │   🐳 Node-RED     │
              │  (Dashboard Web)  │
              │                   │
              │  📊 Gauges        │
              │  📈 Gráficos      │
              │  🔌 Botões Relés  │
              │  📡 Status Real   │
              └───────────────────┘
```

---

## Estrutura de arquivos

```text
~/Projetos/residencial/
├── esp.py              # Código do ESP32 MESTRE (sensores + AP + servidor)
├── escravo.py          # Código do ESP32 ESCRAVO (relés + servidor)
├── bh1750.py           # Biblioteca sensor de luz BH1750
├── aht21.py            # Biblioteca sensor temperatura/umidade AHT21
├── ens160.py           # Biblioteca sensor qualidade ar ENS160
├── mfrc522.py          # Biblioteca leitor RFID MFRC522
├── tracker.py          # Biblioteca sensor IR de presença
├── hcsr04.py           # Biblioteca sensor ultrassônico HC-SR04
├── simple.py           # Biblioteca MQTT (umqtt.simple)
└── README.md           # Este arquivo
```

---

## Hardware utilizado

### ESP32 mestre

| Sensor/Atuador | Pino ESP32 | Protocolo |
|----------------|-----------|-----------|
| HC-SR04 Trigger | GPIO 27 | Digital |
| HC-SR04 Echo | GPIO 14 | Digital |
| BH1750 (Luz) | GPIO 22 (SCL) | I2C |
| AHT21 (Clima) | GPIO 21 (SDA) | I2C |
| ENS160 (Ar) | GPIO 22/21 | I2C |
| MFRC522 (RFID) | GPIO 18 (SCK) | SPI |
| MFRC522 (RFID) | GPIO 23 (MOSI) | SPI |
| MFRC522 (RFID) | GPIO 19 (MISO) | SPI |
| MFRC522 (RFID) | GPIO 5 (CS) | SPI |
| MFRC522 (RFID) | GPIO 4 (RST) | SPI |
| Tracker IR | GPIO 26 | Digital |

### ESP32 escravo

| Atuador | Pino ESP32 | Tipo |
|---------|-----------|------|
| Ar Condicionado | GPIO 13 | Relé (LOW = ligado) |
| Luz Cozinha | GPIO 14 | Relé (LOW = ligado) |
| Luz Sala | GPIO 17 | Relé (LOW = ligado) |
| Luzes Externas | GPIO 18 | Relé (LOW = ligado) |

---

## Funcionalidades implementadas

### ESP32 mestre (192.168.4.1)

| Funcionalidade | Status | Descrição |
|---------------|--------|-----------|
| Rede WiFi AP | ✅ Funcionando | Cria rede `ESP_SANTANA` (senha: `12345678`) |
| Servidor Web | ✅ Funcionando | Painel HTML com dados dos sensores |
| Sensor Ultrassônico | ✅ Funcionando | Mede distância, controla luz da sala |
| Sensor de Luz | ⚠️ Não detectado | I2C scan vazio - verificar conexões |
| Sensor AHT21 | ⚠️ Não detectado | I2C scan vazio - verificar conexões |
| Sensor ENS160 | ⚠️ Não detectado | I2C scan vazio - verificar conexões |
| Sensor RFID | ❌ Pendente | Biblioteca presente, não testado |
| Sensor IR | ✅ Funcionando | Detecta presença, controla luz externa |
| Comando HTTP | ✅ Funcionando | Envia comandos para escravo via HTTP |
| MQTT | ❌ Offline | Aguardando conexão com internet |

### ESP32 escravo (192.168.4.2)

| Funcionalidade | Status | Descrição |
|---------------|--------|-----------|
| Conexão WiFi | ✅ Funcionando | Conecta como cliente na rede do mestre |
| Servidor Web | ✅ Funcionando | Planta baixa interativa com botões |
| Controle Manual | ✅ Funcionando | Botões LIGAR/DESLIGAR no navegador |
| Controle Automático | ✅ Funcionando | Aceita comandos HTTP do mestre |
| Rotas Duplas | ✅ Funcionando | `/ar/on` (manual) e `/rele/ar/ON` (mestre) |
| Status Visual | ✅ Funcionando | Mostra estado atual (LIGADO/DESLIGADO) |

### Node-RED Dashboard

| Componente | Status | Descrição |
|-----------|--------|-----------|
| Broker MQTT | ✅ Configurado | HiveMQ público (`broker.hivemq.com`) |
| Gauges | ✅ Funcionando | Temp, Umidade, CO2, Luminosidade |
| Textos | ✅ Funcionando | TVOC, AQI, Distância, Presença, RFID |
| Gráficos | ✅ Funcionando | Histórico temporal dos sensores |
| Botões Relés | ✅ Funcionando | 8 botões (ON/OFF para cada cômodo) |
| Status Relés | ✅ Funcionando | Feedback visual do estado |
| Simulador | ✅ Funcionando | Dados fake a cada 5 segundos |

---

## Como executar

### 1. Preparar o Node-RED

```bash
npm install -g node-red
node-red
```

- Acessar: `http://localhost:1880`
- Importar o JSON do flow
- Deploy
- Dashboard: `http://localhost:1880/ui`

### 2. Enviar código para o mestre

```bash
mpremote cp esp.py :main.py
mpremote cp aht21.py :aht21.py
mpremote cp ens160.py :ens160.py
mpremote cp bh1750.py :bh1750.py
mpremote cp mfrc522.py :mfrc522.py
mpremote cp tracker.py :tracker.py
mpremote cp hcsr04.py :hcsr04.py
mpremote cp simple.py :simple.py
mpremote reset
```

### 3. Enviar código para o escravo

```bash
mpremote cp escravo.py :main.py
mpremote reset
```

### 4. Acessar

- Mestre (sensores): conectar na rede `ESP_SANTANA` → `http://192.168.4.1`
- Escravo (relés): `http://192.168.4.2`
- Node-RED Dashboard: `http://localhost:1880/ui`

---

## Fluxo de automação

```text
Sensor IR detecta movimento
    │
    ▼
Mestre: leituras["presenca"] = "DETECTADO"
    │
    ▼
Mestre: enviar_comando_http("externa", "ON")
    │
    ▼
Escravo: recebe GET /rele/externa/ON
    │
    ▼
Escravo: Pin(18).value(0) → Luz externa LIGA
```

---

## Problemas conhecidos

| Problema | Status | Solução |
|----------|--------|---------|
| Sensores I2C não detectados | 🔴 Pendente | Verificar conexões físicas, alimentação 3.3V |
| RFID não testado | 🟡 Pendente | Biblioteca presente, aguardando teste |
| MQTT offline | 🟡 Pendente | ESPs sem internet, usar HiveMQ quando disponível |
| Node-RED usa dados simulados | 🟡 Pendente | Conectar ESPs ao MQTT quando tiver internet |

---

## Próximos passos

1. Depurar sensores I2C, verificando conexões físicas do BH1750, AHT21 e ENS160.
2. Testar o RFID conectando o módulo MFRC522.
3. Integrar MQTT com o Node-RED via HiveMQ.
4. Substituir os dados simulados por dados reais no dashboard final.

---

## Comandos úteis

```bash
mpremote fs ls
mpremote fs rm main.py
mpremote
mpremote exec "from machine import Pin, I2C; i2c=I2C(0,scl=Pin(22),sda=Pin(21)); print(i2c.scan())"
```

---

## Nota de segurança

Os terminais COM, NO (Normally Open) e NC (Normally Closed) do módulo de relé conectam-se aos aparelhos de 110V/220V. Cuidado: tensão de rede é perigosa.

---

## Como instalar e rodar

### 1. Preparando o ESP32

Certifique-se de que o seu ESP32 está rodando o firmware oficial do MicroPython. Baixe o firmware genérico para ESP32:

- Firmware oficial: [micropython.org/download/ESP32_GENERIC/](https://micropython.org/download/ESP32_GENERIC/)
- Versão recomendada: `esp32-20241129-v1.24.1.bin`

### 2. Configurando o projeto

Abra o arquivo `main.py` e altere as credenciais do Wi-Fi, se desejar:

```python
SSID = "FungicosESP"
PASSWORD = "SuaSenhaSeguraAbaixo"
DOMAIN_NAME = "fungicos"
```

### 3. Enviando o código para a placa

Recomenda-se o uso do utilitário `mpremote` (oficial do MicroPython). No terminal, navegue até a pasta do projeto:

```bash
mpremote connect /dev/ttyACM0 cp main.py :main.py
mpremote connect /dev/ttyACM0 reset
```

Substitua `/dev/ttyACM0` pela porta serial correta:
- Linux: `/dev/ttyACM0`, `/dev/ttyUSB0`
- Windows: `COM3`, `COM4`
- macOS: `/dev/cu.usbmodem*`, `/dev/cu.usbserial*`

---

## Como usar

1. No celular ou computador, abra as configurações de Wi-Fi.
2. Busque pelas redes disponíveis e conecte-se à rede `FungicosESP`.
3. Use a senha configurada, padrão `12345678`.
4. Abra um navegador web.
5. Digite `http://fungicos.local` ou `http://192.168.4.1` em dispositivos sem suporte a mDNS.
6. Use os botões no painel para ligar e desligar os aparelhos.

---

## Licença

Este projeto é de código aberto e livre para modificações. Sinta-se à vontade para clonar, alterar e adaptar para a sua própria casa. Não há garantias de nenhum tipo.

---

## Simulação no Wokwi

Antes de soldar componentes, você pode simular todo o projeto no **Wokwi**, um simulador de eletrônica online gratuito e open-source.

### Acessando o Wokwi

- Site oficial: [wokwi.com](https://wokwi.com)
- Documentação PT-BR: [docs.wokwi.com/pt-BR/](https://docs.wokwi.com/pt-BR/)
- Template ESP32 + MicroPython: [wokwi.com/projects/new/esp32](https://wokwi.com/projects/new/esp32)

### Componentes equivalentes no Wokwi

| Componente real | Componente no Wokwi | Observação |
| :--- | :--- | :--- |
| ESP32 NodeMCU-32S | `esp32` | Placa padrão, já vem com USB virtual |
| Módulo de Relé 4CH | `relay` ou `led` | Wokwi não tem módulo de relé 4CH nativo |
| Cabo Jumper | Conexões automáticas | Arraste e conecte nos terminais |
| Fonte 5V | USB virtual do ESP32 | Alimentação embutida na simulação |

### Configurando o `diagram.json`

No Wokwi, o circuito é definido no arquivo `diagram.json`. Exemplo para ESP32 + 4 LEDs substituindo relés:

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

### Executando a simulação

1. Acesse [wokwi.com](https://wokwi.com) e clique em New Project → ESP32.
2. Substitua o código em `main.py` pelo código do seu projeto.
3. Clique no botão Play para iniciar a simulação.
4. O console serial aparece no painel inferior.
5. Para testar o servidor web, o Wokwi não simula rede Wi-Fi AP. Use LEDs como substituição visual do estado dos relés.

### Projetos de referência no Wokwi

| Projeto | Link | Descrição |
| :--- | :--- | :--- |
| ESP32 + Relay + MicroPython | [wokwi.com/projects/404221238356318209](https://wokwi.com/projects/404221238356318209) | Controle de relé simples com MicroPython |
| ESP32 + DHT22 + Relay | [wokwi.com/projects/414570544360045569](https://wokwi.com/projects/414570544360045569) | Sensor de temperatura + controle de relé |
| ESP32 Access Point + Relay | [wokwi.com/projects/387095279849004033](https://wokwi.com/projects/387095279849004033) | AP + controle de LED/relé |

---

## Instalação do mpremote e esptool

Antes de enviar o código, instale as ferramentas no seu computador.

### Instalar mpremote

O `mpremote` é o utilitário oficial do MicroPython para controlar dispositivos remotamente.

Pré-requisito: Python 3.8+ instalado no sistema.

```bash
pip install mpremote
```

Se o comando falhar:

```bash
python -m pip install mpremote
pip3 install mpremote
```

Verificar instalação:

```bash
mpremote --help
```

### Instalar esptool

O `esptool` é a ferramenta oficial da Espressif para apagar e gravar firmware no ESP32.

#### Linux

Opção 1:

```bash
pip install esptool
```

Opção 2:

```bash
sudo apt update
sudo apt install python3-serial python3-pip
pip3 install esptool
```

Opção 3:

```bash
sudo snap install espressif-esptool
sudo snap alias espressif-esptool.esptool esptool
sudo snap connect espressif-esptool:raw-usb
sudo snap connect espressif-esptool:serial
```

#### Arch Linux / Manjaro / EndeavourOS

Opção 1:

```bash
pip install esptool
```

Opção 2:

```bash
yay -S esptool
yay -S esptool-git
```

Opção 3:

```bash
sudo pacman -Sy
sudo pacman -S esptool
```

#### Fedora

Opção 1:

```bash
pip install esptool
```

Opção 2:

```bash
sudo dnf makecache --refresh
sudo dnf -y install esptool
```

Opção 3:

```bash
sudo dnf install snapd
sudo snap install espressif-esptool
```

#### Raspberry Pi OS

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

#### Windows

```bash
pip install mpremote esptool
```

Se receber erro de permissão:

```bash
pip install --user mpremote esptool
```

Verificar instalação:

```bash
mpremote --help
esptool.py --version
```

#### macOS

```bash
pip3 install mpremote esptool
```

Ou via Homebrew:

```bash
brew install python
pip3 install mpremote esptool
```

---

## Permissões no Linux

Após instalar, adicione seu usuário ao grupo `dialout` para acessar a porta serial:

```bash
sudo usermod -a -G dialout $USER
```

Reinicie o terminal ou faça logout/login para aplicar as permissões.

Verifique se a porta serial está disponível:

```bash
ls -l /dev/ttyACM*
ls -l /dev/ttyUSB*
```

---

## Dica de versionamento Git

Dentro da pasta do projeto:

```bash
git init
git add main.py README.md
git commit -m "Versão final: Web server em arquivo único com Dashboard CSS Grid e mDNS"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
git push -u origin main
```

---

## Perguntas frequentes

### O que é o ESP32?

O ESP32 é um microcontrolador de baixo custo e alto desempenho da Espressif Systems. Ele possui Wi-Fi 802.11 b/g/n e Bluetooth 4.2 + BLE nativos, opera em 3.3V e inclui dois núcleos Tensilica LX6 de até 240 MHz nas versões mais comuns. Também oferece GPIO, SPI, I2C, I2S, ADC, DAC, PWM, sensor de toque e sensor Hall.

Documentação oficial: [espressif.com/en/products/socs/esp32](https://www.espressif.com/en/products/socs/esp32)

### Links oficiais do MicroPython

MicroPython é uma reescrita otimizada da linguagem Python 3 para microcontroladores.

| Recurso | Link |
| :--- | :--- |
| Site oficial | [micropython.org](https://micropython.org/) |
| Documentação oficial | [docs.micropython.org](https://docs.micropython.org/en/latest/) |
| Firmware ESP32 genérico | [micropython.org/download/ESP32_GENERIC/](https://micropython.org/download/ESP32_GENERIC/) |
| Referência GPIO | [docs.micropython.org/en/latest/library/machine.Pin.html](https://docs.micropython.org/en/latest/library/machine.Pin.html) |
| mpremote | [docs.micropython.org/en/latest/reference/mpremote.html](https://docs.micropython.org/en/latest/reference/mpremote.html) |

### Como formatar e instalar o firmware

Use `esptool` no terminal.

**Apagar flash:**

```bash
esptool.py --port /dev/ttyACM0 erase_flash
```

**Gravar firmware:**

```bash
esptool.py --chip esp32 --port /dev/ttyACM0 --baud 460800 write_flash -z 0x1000 esp32-20241129-v1.24.1.bin
```

### Explicação do código

**Importações iniciais**

```python
from machine import Pin
import network
import socket
import time
```

- `Pin`: controla portas físicas do ESP32.
- `network`: gerencia Wi-Fi.
- `socket`: cria o servidor web.
- `time`: gera pausas e evita travamentos.

**Configurações e dicionário de dispositivos**

```python
SSID = "ESP_SANTANA"
PASSWORD = "12345678"
DOMAIN_NAME = "fungicos"

dispositivos = {
    "ar": {"pin": Pin(21, Pin.OUT, value=1), "nome": "Ar Condicionado"},
}
```

- `SSID` e `PASSWORD`: nome e senha da rede Wi-Fi criada.
- `DOMAIN_NAME`: nome para acesso via `http://fungicos.local`.
- `Pin(21, Pin.OUT, value=1)`: define o pino como saída; iniciar em `1` evita que relés ativos em LOW liguem sozinhos.

**Configuração do Wi-Fi como Access Point**

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

- `network.hostname`: registra o nome na rede.
- `AP_IF`: o ESP32 atua como ponto de acesso.
- `ap.config(...)`: define nome, senha e autenticação.
- O loop garante que o Wi-Fi esteja ativo antes de continuar.

**Interface gráfica em HTML/CSS**

```python
def html_dashboard():
    return """<!DOCTYPE html> ... """
```

A função devolve a página que o navegador renderiza. O HTML e o CSS são entregues diretamente pela aplicação para reduzir complexidade e evitar arquivos extras.

**Servidor web e loop principal**

```python
addr = socket.getaddrinfo("0.0.0.0", 80)[-1]
server = socket.socket()
server.bind(addr)
server.listen(5)
```

Isso prepara a placa para receber requisições HTTP na porta 80.

```python
while True:
    try:
        client, client_addr = server.accept()
        request = str(client.recv(1024))
```

O servidor espera uma conexão de navegador e lê a requisição recebida.

```python
        if "/ar/on" in request:
            dispositivos["ar"]["pin"].value(0)
        elif "/ar/off" in request:
            dispositivos["ar"]["pin"].value(1)
```

Se a rota indicar ligar, o pino vai para `0` e o relé ativa. Se indicar desligar, o pino volta para `1`.

```python
        response = html_dashboard()
        client.send("HTTP/1.1 200 OK\r\n")
        client.send("Content-Type: text/html\r\n")
        client.send("Connection: close\r\n\r\n")
        client.send(response)
        client.close()
```

A resposta HTTP é enviada e a conexão é encerrada.

```python
    except Exception as e:
        print("Erro de comunicação:", e)

    time.sleep(0.01)
```

O `try/except` evita que o programa caia em erros de conexão. O `sleep(0.01)` ajuda a manter o loop estável.

---

## Referências técnicas

| Tópico | Documento | Link |
| :--- | :--- | :--- |
| MicroPython ESP32 | Docs oficiais | [docs.micropython.org/en/latest/esp32/](https://docs.micropython.org/en/latest/esp32/) |
| GPIO MicroPython | `machine.Pin` | [docs.micropython.org/en/latest/library/machine.Pin.html](https://docs.micropython.org/en/latest/library/machine.Pin.html) |
| mpremote | Docs oficiais | [docs.micropython.org/en/latest/reference/mpremote.html](https://docs.micropython.org/en/latest/reference/mpremote.html) |
| esptool | Docs Espressif | [docs.espressif.com/projects/esptool](https://docs.espressif.com/projects/esptool/en/latest/esp32/) |
| Wokwi Simulator | Docs oficiais | [docs.wokwi.com/pt-BR/](https://docs.wokwi.com/pt-BR/) |
| ESP32 GPIO | API Reference | [docs.espressif.com/projects/arduino-esp32/en/latest/api/gpio.html](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/gpio.html) |
| ESP32 GPIO Pins Guide | uPyEasy | [upesy.com/blogs/tutorials/micropython-gpio-pins-of-esp32-usage](https://www.upesy.com/blogs/tutorials/micropython-gpio-pins-of-esp32-usage) |
