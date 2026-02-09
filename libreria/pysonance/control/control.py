from pysonance.const import *
from pysonance.signal import *
from pysonance.control.knob import *
import numpy as np
from copy import copy

# TODO revisar
class FromToIn(Signal):
    '''
    Define una linea recta que pasa por n puntos

    Recibe lista de alturas (knobs)
    Lista de tiempos (s) (knobs)
    ''' 
    def __init__(self, amps:list, times:list):
        super().__init__()
        # assert len(times) == len(amps) - 1
        self.knob_frame = 0
        self.amps = []
        for a in amps:
            self.amps.append(K(a))
        
        self.times = []
        old_t = K(0)
        for t in times:
            self.times.append(K(t) + old_t) 
        
    def fun(self, tiempo):
        _in = False
        pos = [] # lista de las posiciones entre las que se encuentra el frame
        _tfrom = self.tiempo[0]
        _tto = self.tiempo[-1]
        cola = np.array([])
        
        # caso 1, si nos pasamos
        if _tfrom >= self.times[-1].next(self.knob_frame):
            return np.full(len(tiempo), self.amps[-1].next(self.knob_frame))
        
        # caso 2, estamos dentro de los limites
        _p = 0
        for t in self.times:
            _t = t.next(self.knob_frame)
            if _tfrom >= _t:
                pos.append((self.amps[_p], self.amps[_p+1], self.times[_p]))
            if _tto > _t:
                break # parar
            _p += 1
        
        interval = np.array([]) 
        for _p in range(len(pos)):
            _a0, _a1, _t = pos[_p]
            interval = np.concatenate(_a0, _a1, _t)
            
        # caso 3, acabamos pasandonos
        if _tto > self.times[-1].next(self.knob_frame):
            cola = np.full(len(tiempo), self.amps[-1].next(self.knob_frame))    
        
        interval = np.concatenate(interval, cola)
        
        self.knob_frame += 1
        return super().fun(tiempo)

    def fromtoin(self, a0:Knob, a1:Knob, t:Knob):
        ''' devuelve una linea (array) de a0 a a1 en longitud t'''
        _a0 = a0.next(self.knob_frame)
        _a1 = a1.next(self.knob_frame)
        _t = int(t.next(self.knob_frame) * SRATE)
        return np.linspace(_a0, _a1, _t)
    
    def reset(self):
        super().reset()
        self.knob_frame = 0

# TODO revisar
class ADSR(Signal):
    ''' Envolvente ADSR basica'''
    def __init__(self, amp=K(1), A=K(0.1), D=K(0.1), S=K(0.7), R=K(0.2)):
        super().__init__()
        self.amp = amp
        self.A = A # t
        self.D = D # a
        self.S = S # a
        self.R = R # t
        self.knob_frame = 0
        self.last_on = 0
        self.state = State.OFF
        
        self._note_on = FromToIn(
            amps=[0, self.amp, self.S],
            times=[self.A, self.D]
        )
        self._note_rel = FromToIn(
            amps=[self.S, 0],
            times=[self.R]
        )
    
    def fun(self, tiempo):
        if self.state == State.OFF:
            return np.zeros(len(tiempo))
        elif self.state == State.ON: # note on
            self.knob_frame += 1
            self.last_on = self.frame
            return self._note_on.next(tiempo)
        elif self.state == State.RELEASE: # note off
            self.knob_frame += 1
            if self.last_on + self.R.next(self.knob_frame):
                self.state = State.OFF
                self.reset()
            return self._note_rel.next(tiempo)
        return np.zeros(len(tiempo))
    
    def reset(self):
        super().reset()
        self.knob_frame = 0
        
    def on(self):
        self.state = State.ON
        
    def off(self):
        self.frame = 0
        self.state = State.OFF

# TODO REVISAR            
class Gate(Signal):
    ''' Pasa self.true si es mayor que el threshold, si no pasa self.false'''
    def __init__(self, signal, threshold=0, true=1, false=0):
        super().__init__()
        self.signal = C(signal)
        self.threshold = C(threshold)
        self.true = C(true)
        self.false = C(false)
        
    def fun(self, tiempo):
        _thresh = self.threshold.next(tiempo)
        _sig = self.signal.next(tiempo)
        _true = self.true.next(tiempo)
        _false = self.false.next(tiempo)
        return np.where(_sig >= _thresh, _true, _false)
    
class Env(Signal):
    ''' Envolvente basica (sample) que se activa con on() y desactiva con off()'''
    def __init__(self, on_signal=1):
        super().__init__()
        self.state = State.OFF
        self.on_signal = C(on_signal)
        
    def fun(self, tiempo):
        _on = self.on_signal.next(tiempo)
        if self.state == State.OFF:
            return np.zeros(len(tiempo))
        else:
            return self.on_signal.next(tiempo)
    
    def on(self):
        self.state = State.ON
        
    def off(self):
        self.frame = 0
        self.state = State.OFF