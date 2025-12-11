from audio.const import *
from audio.signal import *
import numpy as np

# señales que en principio deben usarse para controlar otras señales y el sonido

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
        self.state = State.STOP
        self.on_signal = C(on_signal)
        
    def fun(self, tiempo):
        _on = self.on_signal.next(tiempo)
        if self.state == State.STOP:
            return np.zeros(len(tiempo))
        else:
            return self.on_signal.next(tiempo)
    
    def on(self):
        self.state = State.PLAY
        
    def off(self):
        self.frame = 0
        self.state = State.STOP
    
        
        