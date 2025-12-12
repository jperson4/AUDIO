import numpy as np
from audio.const import *
from audio.signal import *


class Wavetable(Signal):
    ''' 
        Wavetable, reproduce una onda dada en bucle
        segun una frecuencia amplitud y fase dadas
        
        Para minimizar 
    '''
    def __init__(self, table: np.ndarray, freq=1, amp=1, phase=0, crossfade=0, num_osc=1):
        super().__init__()
        self.num_osc = num_osc
        if crossfade > 0:
            self.table = self.cicletable(table, crossfade)
        else:
            self.table = table
        self.freq = C(freq)
        self.amp = C(amp)
        self.phase = C(phase)
        
        
    def cicletable(self, table: np.ndarray, crossfade) -> np.ndarray:
        ''' Asegura que la tabla ciclará bien haciendo crossfade entre el final y el principio '''
        mid = self.find_point_0(table)
        mid = len(table)//self.num_osc
        
        main = table[:mid] # primera mitad de la tabla
        cross = table[mid: mid + crossfade] # parte a mezclar

        c10 = np.linspace(1, 0, crossfade) # 1 a 0
        c01 = np.linspace(0, 1, crossfade) # 0 a 1

        main[:crossfade] = main[:crossfade] * c01 + cross * c10
        return main
    
    def find_point_0(self, table):
        ''' Encuentra el punto más cercano a 0'''
        mid = len(table) //self.num_osc
        pos = mid
        best_amp = abs(table[mid])
        for offset in range(-10, 10):  # buscar en un rango alrededor del medio
            i = len(table) // 2 + offset # índice actual
            if abs(table[i]) < best_amp:
                best_amp = abs(table[i])
                pos = i
        return pos

        
    def fun(self, tiempo):
        _freq = self.freq.next(tiempo)  # para que freq esté en Hz
        _amp = self.amp.next(tiempo) 
        _phase = self.phase.next(tiempo)
        
        # indices para hacer la interpolación
        indices = (_freq * tiempo) + _phase
        indices = np.mod(indices, len(self.table)) 
        _out = np.interp(indices, np.arange(len(self.table)), self.table)
        return _amp * _out

class WT(Wavetable):
    ''' 
        Sampler simple, reproduce un array de numpy en bucle,
        podemos contrlolar la frecuencia, la amplitud y la fase
        Sería una especie de wavetable
        
        En caso de samplear ondas (usandolo como wavetable), lo mejor es usar frecuencia 1 
        ya que habrá una buena resolución y ciclará bien.
    '''
    def __init__(self, table: np.ndarray, freq=1, amp=1, phase=0, crossfade=10):
        super().__init__(table, freq, amp, phase, crossfade)

class Sampler(Signal):
    ''' 
        Reproduce un array de numpy como si fuera una señal
        cuando acaba, puede volver a empezar (loop=True) o pararse (loop=False)
        se puede saber si está sonando o no con play=True/False
    '''
    def __init__(self, sample: np.ndarray, speed=1, loop=False, play=True):
        super().__init__()
        self.sample = sample
        self.speed = C(speed)
        self.loop = loop
        if loop:
            self.sample = np.concatenate((self.sample, self.sample[:1]))
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
            # if _pos[-1] >= len(self.sample):
            #     self.frame = int(_pos[-1]) % len(self.sample) # volver atras el frame
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