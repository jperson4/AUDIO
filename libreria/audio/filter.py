from audio.const import *
from audio.signal import *
import numpy as np

class Filter(Signal):
    def __init__(self, input:Signal=None, alpha=C(1), state=State.PLAY):
        super().__init__()
        self.alpha=alpha
        self.state = state
        self.input = input
        
    def fun(self, tiempo):
        _alpha = self.alpha.next(tiempo)
        _input = self.input.next(tiempo)
        if self.state != State.PLAY:
            return _input
        
        _filtered_input = self.filter(_input)
        return _input * (1 - _alpha) + _filtered_input * _alpha

class LP(Signal):
    def __init__(self, input:Signal, alpha=C(1), state=State.PLAY):
        super().__init__()
        self.input=input
        self.alpha=alpha
        self.state = state
        self.mem = 0 # last number
        
    def fun(self, tiempo):
        _sig = self.input.next(tiempo)
        _fsig = np.zeros(len(tiempo))
        _alpha = self.alpha.next(tiempo)
        _a0 = _alpha
        
        if self.state != State.PLAY:
            return _sig
        
        if not isinstance(_alpha, (int, float)):
            _a0 = _alpha[0]
        
        _fsig[0] = self.mem + _a0 * (_sig[0] - self.mem)
        for i in range(1, len(tiempo)):
            _fsig[i] = _sig[i-1] + _alpha * (_sig[i] - _sig[i-1])
        return _fsig
        
    
class LP2(Filter):
    def __init__(self, input:Signal=None, alpha=C(1), p=2, state=State.PLAY):
        super().__init__(input, alpha, state)
        self.p = p
        self.weights = np.ones(p)/p
        self.mem = np.zeros(p-1)
        
    def filter(self, input):
        _sig = np.concatenate((self.mem, input))
        self.mem = _sig[-(self.p-1):] # toma los ultimos p elementos de sig
        _fsig = np.convolve(_sig, self.weights, mode='valid')
        _fsig = _fsig[-len(input):]
        return _fsig

        