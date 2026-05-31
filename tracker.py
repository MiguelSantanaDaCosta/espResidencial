"""
line_tracker.py - Biblioteca MicroPython para sensor tracker de linha IR
Detecta linha preta em fundo branco (ou vice-versa)
Compatível com: KY-033, HW-201, TCRT5000, módulos line follower
"""

from machine import Pin, ADC
import time


class LineTracker:
    """
    Sensor tracker de linha IR de canal único
    Detecta presença de linha preta em fundo branco
    """
    
    # Estados do sensor
    NO_LINE = 0      # Não detecta linha (fundo branco)
    LINE_DETECTED = 1  # Detecta linha preta
    
    def __init__(self, pin, pin_type=Pin.IN, use_pull=True):
        """
        Inicializa o sensor tracker de linha
        
        Parâmetros:
            pin: Pino GPIO conectado ao sensor (OUTPUT do sensor)
            pin_type: Tipo de pino (IN para digital, ADC para analógico)
            use_pull: Usa resistor pull-up/pull-down (True para KY-033)
        """
        self.pin_type = pin_type
        
        if pin_type == Pin.IN:
            # Modo digital (SAída DO do sensor)
            if use_pull:
                self.sensor = Pin(pin, Pin.IN, Pin.PULL_DOWN)
            else:
                self.sensor = Pin(pin, Pin.IN)
        else:
            # Modo analógico (SAída AO do sensor - com potenciômetro)
            self.sensor = ADC(pin)
        
        # Configurações
        self.inverted = False  # Se True, inverte a lógica
        self.threshold = 2048  # Threshold para modo analógico (0-4095)
    
    def read(self):
        """
        Lê o estado do sensor
        
        Returns:
            int: 0 se não detecta linha, 1 se detecta linha (modo digital)
            int: Valor analógico 0-4095 (modo analógico)
        """
        if self.pin_type == Pin.IN:
            value = self.sensor.value()
            if self.inverted:
                value = 1 - value
            return value
        else:
            return self.sensor.read_u16() >> 4  # Converte para 0-4095
    
    def is_line_present(self):
        """
        Verifica se há linha presente
        
        Returns:
            bool: True se linha detectada, False se não houver
        """
        if self.pin_type == Pin.IN:
            return self.read() == 1
        else:
            # Modo analógico: linha preta = valor baixo (< threshold)
            return self.read() < self.threshold
    
    def detect(self):
        """
        Alias para is_line_present()
        
        Returns:
            bool: True se linha detectada
        """
        return self.is_line_present()
    
    def set_inverted(self, inverted=True):
        """
        Inverte a lógica do sensor
        
        Usar se o sensor estiver funcionando ao contrário:
        - True: linha preta = 0, fundo branco = 1
        - False: linha preta = 1, fundo branco = 0
        
        Args:
            inverted: Se True, inverte a lógica
        """
        self.inverted = inverted
    
    def set_threshold(self, threshold):
        """
        Define threshold para modo analógico
        
        Args:
            threshold: Valor entre 0-4095 (padrão: 2048)
        """
        self.threshold = max(0, min(4095, threshold))
    
    def calibrate(self, samples=10):
        """
        Calibra o threshold automaticamente tirando média
        
        Args:
            samples: Número de amostras para calibração
            
        Returns:
            int: Threshold calculado
        """
        values = []
        for _ in range(samples):
            values.append(self.read())
            time.sleep_ms(50)
        
        avg = sum(values) / len(values)
        self.threshold = int(avg)
        return self.threshold


class LineTrackerMulti:
    """
    Sensor tracker de linha IR multi-canal (3, 5, 6 ou 8 sensores)
    Para robôs suítores de linha avançados
    
    Suporta: KY-033 xN, módulos line follower 3/5/6/8 canais
    """
    
    # Padrões de detecção
    ALL_WHITE = 0b00000000  # Todos sensores em fundo branco
    ALL_BLACK = 0b11111111  # Todos sensores em linha preta
    
    def __init__(self, pin_list, pin_type=Pin.IN, inverted=False):
        """
        Inicializa múltiplos sensores tracker de linha
        
        Parâmetros:
            pin_list: Lista de pinos GPIO [pino_esquerda, ..., pino_direita]
            pin_type: Tipo de pino (IN para digital, ADC para analógico)
            inverted: Se True, inverte lógica para todos os sensores
        """
        self.num_sensors = len(pin_list)
        self.pins = []
        self.inverted = inverted
        
        # Cria lista de objetos LineTracker
        for i, pin in enumerate(pin_list):
            tracker = LineTracker(pin, pin_type, use_pull=True)
            tracker.inverted = inverted
            self.pins.append(tracker)
        
        # Posição calculada (para seguimento de linha PID)
        self.position = 0
    
    def read_all(self):
        """
        Lê todos os sensores
        
        Returns:
            list: Lista de estados [s0, s1, s2, ...] onde 0=branco, 1=preto
        """
        return [pin.is_line_present() for pin in self.pins]
    
    def read_binary(self):
        """
        Lê todos os sensores como valor binário
        
        Returns:
            int: Valor binário onde cada bit é um sensor
                 Ex: 0b0011100 = sensores 2,3,4 na linha
        """
        states = self.read_all()
        value = 0
        for i, state in enumerate(states):
            if state:
                value |= (1 << i)
        return value
    
    def get_sensor(self, index):
        """
        Obtém estado de um sensor específico
        
        Args:
            index: Índice do sensor (0 = esquerda, n-1 = direita)
            
        Returns:
            bool: True se sensor detecta linha
        """
        if 0 <= index < self.num_sensors:
            return self.pins[index].is_line_present()
        return None
    
    def set_sensor(self, index, inverted):
        """
        Configura inversão para sensor específico
        
        Args:
            index: Índice do sensor
            inverted: Se True, inverte lógica desse sensor
        """
        if 0 <= index < self.num_sensors:
            self.pins[index].inverted = inverted
    
    def calculate_position(self):
        """
        Calcula posição da linha para algoritmo PID
        Usado para robôs suítores de linha precisos
        
        Returns:
            float: Posição da linha (-1.0 = tudo esquerda, 1.0 = tudo direita)
        """
        states = self.read_all()
        
        # Peso de cada sensor (esquerda = negativo, direita = positivo)
        weights = [(i - (self.num_sensors - 1) / 2) for i in range(self.num_sensors)]
        
        total_weight = sum(weights[i] for i in range(self.num_sensors) if states[i])
        total_active = sum(1 for state in states if state)
        
        if total_active == 0:
            # Nenhum sensor na linha - mantém última posição ou retorna 0
            self.position = 0
        else:
            self.position = total_weight / total_active
        
        return self.position
    
    def get_direction(self):
        """
        Determina direção para ajustar o robô
        
        Returns:
            str: 'left', 'right', 'center', ou 'lost'
        """
        states = self.read_all()
        active_sensors = [i for i, s in enumerate(states) if s]
        
        if len(active_sensors) == 0:
            return 'lost'  # Perdeu a linha
        
        center = (self.num_sensors - 1) / 2
        avg_position = sum(active_sensors) / len(active_sensors)
        
        if avg_position < center - 0.5:
            return 'left'
        elif avg_position > center + 0.5:
            return 'right'
        else:
            return 'center'
    
    def calibrate_all(self, samples=10):
        """
        Calibra todos os sensores analógicos
        
        Args:
            samples: Amostrast para calibração
        """
        for tracker in self.pins:
            tracker.calibrate(samples)


# === EXEMPLO DE USO - SENSOR ÚNICO ===
if __name__ == "__main__":
    # Sensor único KY-033
    SENSOR_PIN = 15  # Ajuste conforme sua configuração
    
    # Inicializa sensor
    tracker = LineTracker(SENSOR_PIN, Pin.IN, use_pull=True)
    
    print("Sensor Tracker de Linha Inicializado")
    print("Aproxime a linha preta do sensor...\n")
    
    while True:
        if tracker.is_line_present():
            print("✓ Linha detectada!")
        else:
            print("✗ Sem linha (fundo branco)")
        
        time.sleep(0.2)


# === EXEMPLO DE USO - MÚLTIPLOS SENSORES (3 CANAIS) ===
if __name__ == "__main__":
    # 3 sensores KY-033 para robô suítor de linha
    PIN_LIST = [14, 15, 16]  # Esquerda, Centro, Direita
    
    # Inicializa múltiplos sensores
    tracker = LineTrackerMulti(PIN_LIST, Pin.IN, inverted=False)
    
    print(f"{tracker.num_sensors} sensores inicializados")
    print("Robô suítor de linha pronto!\n")
    
    while True:
        # Lê todos os sensores
        states = tracker.read_all()
        binary = tracker.read_binary()
        direction = tracker.get_direction()
        position = tracker.calculate_position()
        
        print(f"Sensores: {states}")
        print(f"Binário: 0b{binary:03b}")
        print(f"Direção: {direction}")
        print(f"Posição: {position:.2f}")
        print("-" * 30)
        
        time.sleep(0.2)


# === EXEMPLO - ROBÔ SUIITOR DE LINHA SIMPLES ===
if __name__ == "__main__":
    from machine import Pin
    import time
    
    # Sensores: Esquerda, Centro, Direita
    SENSOR_pins = [14, 15, 16]
    tracker = LineTrackerMulti(SENSOR_pins, Pin.IN)
    
    # Motores (exemplo com 2 motores DC)
    MOTOR_LEFT_FWD = Pin(2, Pin.OUT)
    MOTOR_LEFT_BWD = Pin(3, Pin.OUT)
    MOTOR_RIGHT_FWD = Pin(4, Pin.OUT)
    MOTOR_RIGHT_BWD = Pin(5, Pin.OUT)
    
    def set_motor_speed(left_speed, right_speed):
        """Configura velocidade dos motores (-1 a 1)"""
        # Esquerda
        if left_speed > 0:
            MOTOR_LEFT_FWD.value(1)
            MOTOR_LEFT_BWD.value(0)
        elif left_speed < 0:
            MOTOR_LEFT_FWD.value(0)
            MOTOR_LEFT_BWD.value(1)
            left_speed = -left_speed
        else:
            MOTOR_LEFT_FWD.value(0)
            MOTOR_LEFT_BWD.value(0)
        
        # Direita
        if right_speed > 0:
            MOTOR_RIGHT_FWD.value(1)
            MOTOR_RIGHT_BWD.value(0)
        elif right_speed < 0:
            MOTOR_RIGHT_FWD.value(0)
            MOTOR_RIGHT_BWD.value(1)
            right_speed = -right_speed
        else:
            MOTOR_RIGHT_FWD.value(0)
            MOTOR_RIGHT_BWD.value(0)
    
    print("Iniciando seguimento de linha...")
    
    while True:
        direction = tracker.get_direction()
        
        # Controle simples P
        if direction == 'left':
            set_motor_speed(0.3, 0.7)  # Vira esquerda
        elif direction == 'right':
            set_motor_speed(0.7, 0.3)  # Vira direita
        elif direction == 'center':
            set_motor_speed(0.6, 0.6)  # Reto
        else:  # 'lost' - perdeu a linha
            set_motor_speed(0.5, 0.5)  # Continua reto procurando
        
        time.sleep(0.05)
