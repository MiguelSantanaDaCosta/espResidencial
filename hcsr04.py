"""
hc_sr04.py - Biblioteca MicroPython para sensor ultrassônico HC-SR04
Mede distância usando tempo de voo do som
"""

from machine import Pin
import time


class HC_SR04:
    """Sensor ultrassônico HC-SR04 para MicroPython"""
    
    SPEED_OF_SOUND = 34300  # cm/s (343 m/s)
    MIN_DISTANCE = 2.0      # cm (mínimo confiável)
    MAX_DISTANCE = 400.0    # cm (máximo do sensor)
    
    def __init__(self, trig_pin, echo_pin):
        """
        Inicializa o sensor HC-SR04
        
        Parâmetros:
            trig_pin: Pino GPIO Trig (disparo)
            echo_pin: Pino GPIO Echo (retorno)
        """
        # Configura pino Trig como output
        self.trig = Pin(trig_pin, Pin.OUT)
        self.trig.value(0)
        
        # Configura pino Echo como input
        self.echo = Pin(echo_pin, Pin.IN)
    
    def _send_pulse(self):
        """Envia pulso de 10µs no Trig"""
        # Garante estado baixo inicial
        self.trig.value(0)
        time.sleep_us(2)
        
        # Pulso de 10µs alto
        self.trig.value(1)
        time.sleep_us(10)
        self.trig.value(0)
    
    def _wait_echo(self, timeout_us=30000):
        """
        Aguarda e mede duração do pulso Echo
        
        Args:
            timeout_us: Tempo máximo de espera (µs)
            
        Returns:
            int: Duração do pulso em µs, ou None se timeout
        """
        # AguardaEcho ficar alto (início do pulso)
        start_wait = time.ticks_us()
        while self.echo.value() == 0:
            if time.ticks_diff(time.ticks_us(), start_wait) > timeout_us:
                return None
        
        # Captura momento inicial
        start_time = time.ticks_us()
        
        # Aguarda Echo ficar baixo (fim do pulso)
        while self.echo.value() == 1:
            elapsed = time.ticks_diff(time.ticks_us(), start_time)
            if elapsed > timeout_us:
                return None
        
        # Retorna duração do pulso
        return time.ticks_diff(time.ticks_us(), start_time)
    
    def measure(self, timeout_us=30000):
        """
        Realiza uma medição de distância
        
        Args:
            timeout_us: Timeout em µs (30000µs = ~4m)
            
        Returns:
            float: Distância em cm, ou None se erro/timeout
        """
        # Envia pulso de disparo
        self._send_pulse()
        
        # Aguarda e mede pulso de retorno
        pulse_duration = self._wait_echo(timeout_us)
        
        if pulse_duration is None:
            return None
        
        # Calcula distância
        # Distância = (tempo × velocidade do som) / 2
        # Dividimos por 2 porque o som vai e volta
        distance_cm = (pulse_duration * self.SPEED_OF_SOUND) / 1000000 / 2
        
        return distance_cm
    
    def measure_cm(self, timeout_us=30000):
        """
        Mede distância em centímetros (alias para measure())
        
        Returns:
            float: Distância em cm ou None se erro
        """
        return self.measure(timeout_us)
    
    def measure_mm(self, timeout_us=30000):
        """
        Mede distância em milímetros
        
        Returns:
            float: Distância em mm ou None se erro
        """
        result = self.measure(timeout_us)
        if result is not None:
            return result * 10
        return None
    
    def measure_average(self, num_samples=5, timeout_us=30000):
        """
        Realiza múltiplas medições e retorna a média
        (reduz ruído e melhora precisão)
        
        Args:
            num_samples: Número de amostras
            timeout_us: Timeout por amostra
            
        Returns:
            float: Média das medições em cm, ou None se todas falharem
        """
        measurements = []
        
        for _ in range(num_samples):
            result = self.measure(timeout_us)
            if result is not None:
                # Filtra valores fora do range válido
                if self.MIN_DISTANCE <= result <= self.MAX_DISTANCE:
                    measurements.append(result)
            
            # Pequeno delay entre medições
            time.sleep_ms(50)
        
        if len(measurements) == 0:
            return None
        
        return sum(measurements) / len(measurements)
    
    def is_valid(self, distance_cm):
        """
        Verifica se uma medição está dentro do range válido
        
        Args:
            distance_cm: Distância medida em cm
            
        Returns:
            bool: True se distância válida
        """
        if distance_cm is None:
            return False
        return self.MIN_DISTANCE <= distance_cm <= self.MAX_DISTANCE
    
    def get_distance_with_retry(self, max_retries=3, timeout_us=30000):
        """
        Tenta medir distância com retries em caso de erro
        
        Args:
            max_retries: Número máximo de tentativas
            timeout_us: Timeout por tentativa
            
        Returns:
            float: Distância em cm ou None se todas tentativas falharem
        """
        for attempt in range(max_retries):
            result = self.measure(timeout_us)
            if self.is_valid(result):
                return result
            time.sleep_ms(20)
        
        return None


