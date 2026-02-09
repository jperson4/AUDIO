from pysonance.const import *
from pysonance.signal import *
import numpy as np
from copy import copy

# señales que en principio deben usarse para controlar otras señales y el sonido
class State(Enum):
    OFF = 0
    ON = 1
    PAUSE = 2
    RELEASE = 3

class Knob:
    ''' 
    Clase como señal pero que no va por chunks sino que devuelve enteros
    (sirve para esos parámetros que cambian una vez cada frame)
    '''
    def __new__(cls, valor):
        ''' De esta forma podemos hacer C(C(1)) y devolverá C(1) sin que haya problemas'''
        if isinstance(valor, Knob):
            return valor
        return super(Knob, cls).__new__(cls)    
    
    def __init__(self, valor=0):
        if not isinstance(valor, Knob):
            super().__init__()
            self.valor = valor
            self.frame = 0

    def next(self, frame=None):
        self.frame = frame if frame is not None else self.frame
        ret = self.fun(self.frame)
        self.frame += 1
        return ret
    
    def __add__(self, other):
        other = K(other)
        return Knob_Add(self, other)
        
    def __sub__(self, other):
        other = K(other)
        return Knob_Sub(self, other)
    
    def __mul__(self, other):
        other = K(other)
        return Knob_Mul(self, other)
    
    def __truediv__(self, other):
        other = K(other)
        return Knob_Div(self, other)
    
    def __neg__(self):
        return Knob_Neg(self)
    
    def __pow__(self, power):
        power = K(power)
        return Knob_Pow(self, power)
    
    def __radd__(self, other):
        other = K(other)
        return Knob_Add(other, self)

    def __rsub__(self, other):
        other = K(other)
        return Knob_Sub(other, self)

    def __rmul__(self, other):
        other = K(other)
        return Knob_Mul(other, self)

    def __rtruediv__(self, other):
        other = K(other)
        return Knob_Div(other, self)

    def __rpow__(self, other):
        other = K(other)
        return Knob_Pow(other, self)
    
    def fun(self, frame):
        return self.value
    
class K(Knob):
    
    def __init__(self, value=0):
        super().__init__(value)
        
class Knob_Add(Signal):
    def __init__(self, a, b):
        super().__init__()
        self.a = a
        self.b = b
        
    def fun(self, frame):
        return self.a.next(frame) + self.b.next(frame)
    
class Knob_Sub(Signal):
    def __init__(self, a, b):
        super().__init__()
        self.a = a
        self.b = b
        
    def fun(self, frame):
        return self.a.next(frame) - self.b.next(frame)

class Knob_Mul(Signal):
    def __init__(self, a, b):
        super().__init__()
        self.a = a
        self.b = b
        
    def fun(self, frame):
        return self.a.next(frame) * self.b.next(frame)
    
class Knob_Div(Signal):
    def __init__(self, a, b):
        super().__init__()
        self.a = a
        self.b = b
        
    def fun(self, frame):
        return self.a.next(frame) / self.b.next(frame)
    
class Knob_Neg(Signal):
    def __init__(self, a):
        super().__init__()
        self.a = a
        
    def fun(self, frame):
        return -self.a.next(frame)
    
class Knob_Pow(Signal):
    def __init__(self, a, power):
        super().__init__()
        self.a = a
        self.power = power
        
    def fun(self, frame):
        return self.a.next(frame) ** self.power.next(frame)


class Trigger(Signal):
    ''' Tiene dos señales (on y off), cuando recibe un trigger cambia entre ambas'''
    def __init__(self, on_signal, off_signal=C(0), reset = False):
        super().__init__()
        self.on_signal = C(on_signal)
        self.off_signal = C(off_signal)
        self.reset = reset
        self.state = False  # False = off_signal, True = on_signal
        
    def fun(self, frame):
        if self.state:
            return self.on_signal.next(frame)
        else:
            return self.off_signal.next(frame)
        
    def trigger(self):
        self.state = not self.state
        if self.reset:
            self.frame = 0
            self.on_signal.reset()
            self.off_signal.reset()
            

    
        
        