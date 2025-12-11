import numpy as np
from audio.const import *
from audio.signal import *

class T(Signal):
    ''' 
        Sampler simple, reproduce un array de numpy en bucle,
        podemos contrlolar la frecuencia, la amplitud y la fase
        Sería una especie de wavetable
    '''
    def __init__(self, table: np.ndarray, freq=1, amp=1, phase=0):
        super().__init__()
        self.table = table
        self.freq = C(freq)
        self.amp = C(amp)
        self.phase = C(phase)
        self.frame = 0 # posicion de la tabla en la que estamos
        
    def fun(self, tiempo):
        _freq = self.freq.next(tiempo) / SRATE  # para que freq esté en Hz
        _amp = self.amp.next(tiempo) 
        _phase = self.phase.next(tiempo)
        
        # indices para hacer la interpolación
        indices = self.frame + (_freq * tiempo) + _phase
        indices = np.mod(indices, len(self.table)) # por si nos pasamos
        _out = np.interp(indices, np.arange(len(self.table)), self.table)
        return _amp * _out



class Sampler(Signal):
    ''' Reproduce un array de numpy como si fuera una señal
        cuando acaba, puede volver a empezar (loop=True) o pararse (loop=False)
        se puede saber si está sonando o no con play=True/False
    '''
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
    
    def start(self):
        self.play = True
        self.frame = 0
        
    def stop(self):
        self.play = False
        self.frame = 0
        
    def pause(self):
        self.play = False
        
    def resume(self):
        self.play = True
        
    def state(self):
        if self.play:
            return State.PLAY
        else:
            if self.frame == 0:
                return State.STOP
            else:
                return State.PAUSE