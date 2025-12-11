from audio.const import *
from audio.signal import *
from audio.filter import *
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
            
class KS(Signal):
    def __init__(self, freq=440, input=Noise(), filter=LP2, filter_p = 2):
        super().__init__()
        self.input = input
        self.filter = filter
        self.out = input
        self.p = 2
        self.dir = 1
    
    def fun(self, tiempo):
        self.frame = 0
        self.p = self.p * (1 + .05 * self.dir)
        if self.p > len(tiempo)-5:
            self.p = len(tiempo) - 6
            self.dir = -1
        elif self.p < 2:
            self.dir = 1
            self.p = 2    
            
        self.out = self.filter(self.input, p=int(self.p))
        return self.out.next(tiempo)
        
class KarpusStrong(Signal):
    # TODO: encontrar la manera de hacer que la frecuencia sea modulable, supongo que tocara cambiar el buffer o yo que se
    def __init__(self, freq=440, input=Noise(), filter=LP2(input=None), factor=10):
        super().__init__()
        self.buffer = input.next(np.arange(0, SRATE//freq)) 
        self.filter = filter
        # self.p = 2
        # self.dir = 1
    
    def fun(self, tiempo):
        _index = np.arange(self.frame-len(tiempo), self.frame) % len(self.buffer)
        _out = self.buffer[_index]
        _fout = self.filter.filter(_out)
        self.buffer[_index] = _fout
        return _fout
        
        