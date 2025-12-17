from pysonance.modules.const import *
import numpy as np

# señales base y operaciones entre señales
class Signal:
    def __init__(self):
        self.frame = 0
        
    ''' Devuelve un chunk de señal '''
    def next(self, tiempo=None):
        _tiempo = tiempo
        if tiempo is None:
            _tiempo = np.arange(self.frame, self.frame + CHUNK)
            self.frame += CHUNK
        elif isinstance(tiempo, (int, float)):
            _tiempo = np.arange(self.frame, self.frame + int(tiempo))
            self.frame += int(tiempo)
        return self.fun(_tiempo)
            
    ''' Función que define la señal '''
    def fun(self, tiempo):
        return np.zeros(len(tiempo))
    
    def reset(self):
        self.frame = 0
        
    # Operadores
    def __add__(self, other):
        other = C(other)
        return Add(self, other)
        
    def __sub__(self, other):
        other = C(other)
        return Sub(self, other)
    
    def __mul__(self, other):
        other = C(other)
        return Mul(self, other)
    
    def __truediv__(self, other):
        other = C(other)
        return Div(self, other)
    
    def __neg__(self):
        return Neg(self)
    
    def __pow__(self, power):
        power = C(power)
        return Pow(self, power)
    
class Add(Signal):
    def __init__(self, a, b):
        super().__init__()
        self.a = a
        self.b = b
        
    def fun(self, tiempo):
        return self.a.next(tiempo) + self.b.next(tiempo)
    
class Sub(Signal):
    def __init__(self, a, b):
        super().__init__()
        self.a = a
        self.b = b
        
    def fun(self, tiempo):
        return self.a.next(tiempo) - self.b.next(tiempo)

class Mul(Signal):
    def __init__(self, a, b):
        super().__init__()
        self.a = a
        self.b = b
        
    def fun(self, tiempo):
        return self.a.next(tiempo) * self.b.next(tiempo)
    
class Div(Signal):
    def __init__(self, a, b):
        super().__init__()
        self.a = a
        self.b = b
        
    def fun(self, tiempo):
        return self.a.next(tiempo) / self.b.next(tiempo)
    
class Neg(Signal):
    def __init__(self, a):
        super().__init__()
        self.a = a
        
    def fun(self, tiempo):
        return -self.a.next(tiempo)
    
class Pow(Signal):
    def __init__(self, a, power):
        super().__init__()
        self.a = a
        self.power = power
        
    def fun(self, tiempo):
        return self.a.next(tiempo) ** self.power.next(tiempo)
    
class Const(Signal):
    def __new__(cls, valor):
        ''' De esta forma podemos hacer C(C(1)) y devolverá C(1) sin que haya problemas'''
        if isinstance(valor, Signal):
            return valor
        return super(Const, cls).__new__(cls)    
    
    def __init__(self, valor: float):
        if not isinstance(valor, Signal):
            super().__init__()
            self.valor = valor
        
    def fun(self, tiempo):
        return self.valor

class C(Const): # otra forma más corta de definir una constante
    '''' Constante '''
    def __init__(self, valor):
        super().__init__(valor)
        
class X(Signal): 
    ''' Función lineal con pendiente y desplazamiento, elevada a una potencia
        (mul*x + add)^pow'''
    def __init__(self, mul=1, add=0, pow=1):
        super().__init__()
        self.mul = C(mul)
        self.add = C(add)
        self.pow = C(pow)
        
    def fun(self, tiempo):
        _mul = self.mul.next(tiempo) / SRATE 
        _add = self.add.next(tiempo)
        _exp = self.pow.next(tiempo)
        return (_mul * tiempo + _add) ** _exp   

class Function(Signal):
    ''' 
    Función genérica que permite definir muchas funciones matemáticas

    Para definir algo como f(x) = arcsin(sin(x^2) - .1) * 2, haríamos:
        g = Function(np.sin, X(pow=C(2)) - C(.1))
        f = Function(np.arcsin, g) * C(2)
        
    (es necesario que function sea una función que acepte un array de numpy como input y devuelva otro array de numpy) 
    '''
    def __init__(self, function, inside=0):
        super().__init__()
        self.inside = C(inside)
        self.function = function
        
    def fun(self, tiempo):
        return self.function(self.inside.next(tiempo))
          
    # Como es un poco complejo, a continuación he desarrollado algunas funciones
    # de onda comunes como Sine, Triangle y Sawtooth. 