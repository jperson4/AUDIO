from audio.const import *
from audio.signal import *
import numpy as np

# osciladores y generadores que devuelven señales que en principio deben usarse para generar sonido

''' 
    Podemos ver la frecuencia como el valor dentro del seno por el cual 
    multiplicamos el tiempo y la fase el valor que sumamos al tiempo*freq.
    
    de esta forma, para hacer algo como sin(sin(x)), haríamos:
        Sine(freq=0, phase=Sine())
    
'''
class Sine(Signal):
    ''' Onda senoidal con frecuencia, amplitud y fase 
        Seria el equivalente a amp * sin( 2*pi* freq * x + phase )
    '''
    def __init__(self, freq=1, amp=1, phase=0):
        super().__init__()
        self.freq = C(freq)
        self.amp = C(amp)
        self.phase = C(phase)
        
    def fun(self, tiempo):
        _freq = self.freq.next(tiempo)
        _freq = _freq / SRATE  # para que freq esté en Hz
        _amp = self.amp.next(tiempo) 
        _phase = self.phase.next(tiempo)
        return _amp * np.sin(2 * np.pi * _freq * tiempo + _phase)
    
class Triangle(Signal):
    ''' Onda triangular con frecuencia, amplitud y fase
        Seria el equivalente a amp * (2/pi) * arcsin( sin( 2*pi* freq * x + phase ) )
    '''
    def __init__(self, freq=1, amp=1, phase=0):
        super().__init__()
        self.freq = C(freq)
        self.amp = C(amp)
        self.phase = C(phase)
        
    def fun(self, tiempo):
        _freq = self.freq.next(tiempo) / SRATE
        _amp = self.amp.next(tiempo) 
        _phase = self.phase.next(tiempo)
        return _amp * (2 / np.pi) * np.arcsin(np.sin(2 * np.pi * _freq * tiempo + _phase))
    
class Sawtooth(Signal):
    ''' Onda diente de sierra con frecuencia, amplitud y fase
        Seria el equivalente a amp * (2/pi) * arctan( tan( pi* freq * x + phase ) )
    '''
    def __init__(self, freq=1, amp=1, phase=0):
        super().__init__()
        self.freq = C(freq)
        self.amp = C(amp)
        self.phase = C(phase)
        
    def fun(self, tiempo):
        _freq = self.freq.next(tiempo) / SRATE
        _amp = self.amp.next(tiempo) 
        _phase = self.phase.next(tiempo)
        return _amp * (2 / np.pi) * np.arctan(np.tan(np.pi * _freq * tiempo + _phase))
    
class Square(Signal):
    ''' Onda cuadrada con frecuencia, amplitud y fase
        Seria el equivalente a amp * sign( sin( 2*pi* freq * x + phase ) )
    '''
    def __init__(self, freq=1, amp=1, phase=0):
        super().__init__()
        self.freq = C(freq)
        self.amp = C(amp)
        self.phase = C(phase)
        
    def fun(self, tiempo):
        _freq = self.freq.next(tiempo) / SRATE
        _amp = self.amp.next(tiempo) 
        _phase = self.phase.next(tiempo)
        return _amp * np.sign(np.sin(2 * np.pi * _freq * tiempo + _phase))
        # return _amp * sg.square(2*np.pi * tiempo * _freq+ _phase)
        
class Noise(Signal):
    ''' Ruido blanco '''
    def __init__(self, amp=C(1)):
        super().__init__()
        self.amp = amp
        
    def fun(self, tiempo):
        _amp = self.amp.next(tiempo) 
        return _amp * np.random.uniform(-1, 1, len(tiempo))
    
class Sampler(Signal):
    ''' Reproduce un array de numpy como si fuera una señal '''
    def __init__(self, sample: np.ndarray, speed=1, loop=False, play=True):
        super().__init__()
        self.sample = sample
        self.speed = C(speed)
        self.loop = loop
        self.play = play
        
    def fun(self, tiempo):
        if not self.play:
            return np.zeros(len(tiempo))
        
        _speed = self.speed.next(tiempo) # cuanto avanzamos en cada muestra
        
        if isinstance(_speed, (int, float)):
            _speed = np.repeat(_speed, len(tiempo))
        _pos = np.cumsum(_speed)
        
        if self.loop:
            _pos = np.mod(_pos, len(self.sample))
        else:
            if np.any(_pos >= len(self.sample)):
                self.play = False
            _pos = np.clip(_pos, 0, len(self.sample)-1)
        
        _indices = np.arange(len(self.sample))
        _out = np.interp(_pos, _indices, self.sample) 
        
        # hay que actualizar el frame para que el tiempo vaya con la velocidad
        self.frame = int(_pos[-1]) + 1
        return _out