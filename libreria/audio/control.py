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