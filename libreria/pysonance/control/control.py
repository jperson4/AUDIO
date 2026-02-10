from pysonance.const import *
from pysonance.signal import *
from pysonance.control.knob import *
import numpy as np

class FromToIn(Signal):
    '''
    Define una linea recta que pasa por n puntos

    Recibe lista de alturas (knobs)
    Lista de tiempos (s) (knobs) (no aditiva)
    ''' 
    def __init__(self, amps:list, times:list):
        super().__init__()
        # assert len(times) == len(amps) - 1
        self.knob_frame = 0
        self.amps = []
        for a in amps:
            self.amps.append(K(a))
        
        self.times = [K(0)]
        old_t = K(0)
        for t in times:
            kt = K(t)
            self.times.append(kt + old_t)
            old_t = kt

        self.times.append(old_t) # TODO por alguna razon funciona con un punto extra al final, revisar

        for t in self.times:
            print(t.next(self.knob_frame))

    def fun(self, tiempo):

        _positions = []
        _tfrom = tiempo[0]
        _tto = tiempo[-1]

        # buscamos los indices de tiempos entre los que se encuentra el frame
        # a0 - t0 - a1 - t1 - a2 - t2 - a3
        # A = [a0, a1, a2, a3]
        # T = [0, t0, t0+t1, t0+t1+t2]

        _ifrom = 0
        _ito = 0

        _in = False

        # caso 0: si nos pasamos desde el principio, devolvemos el ultimo valor
        if _tfrom >= self.times[-1].next(self.knob_frame):
            return np.full(len(tiempo), self.amps[-1].next(self.knob_frame))

        # caso 1: estamos dentro de los limites, buscamos los indices entre los que se encuentra el frame

        amps = []
        times = []

        for t in self.times:
            _tact = t.next(self.knob_frame) * SRATE
            if not _in: # aun no estamos en el rango
                if _tfrom <= _tact: # hemos encontrado el primer punto, guardamos el indice y pasamos a buscar el _to
                    _in = True
                    _ito = _ifrom
                else:
                    _ifrom += 1
            elif _in: # ya estamos en el rango
                amps.append(self.amps[_ito].next(self.knob_frame))
                times.append(self.times[_ito].next(self.knob_frame))
                if _tto < _tact: # nos hemos pasado del ultimo punto, guardamos el indice
                    break
                else: # no hemos llegado al final del rango, seguimos buscando
                    _ito += 1

        ret = np.array([])

        for i in range(len(amps)-1):
            _a0 = amps[i]
            _a1 = amps[i+1]
            _tact = int((times[i+1] - times[i]))
            ret = np.concatenate((ret, self.fromtoin(_a0, _a1, _tact)))

        # caso 2: ya nos hemos pasado del ultimo punto, acopamos el ultimo valor al final del array
        cola = np.array([])
        if times[-1] < _tto:
            cola = np.full(len(tiempo) - len(ret), amps[-1])

        self.knob_frame += 1

        return np.concatenate((ret, cola))

    def fromtoin_knob(self, a0:Knob, a1:Knob, t:Knob):
        ''' devuelve una linea (array) de a0 a a1 en longitud t'''
        _a0 = a0.next(self.knob_frame)
        _a1 = a1.next(self.knob_frame)
        _t = int(t.next(self.knob_frame) * SRATE)
        return np.linspace(_a0, _a1, _t)
    
    def fromtoin(self, a0, a1, t):
        _t = int(t * SRATE)
        ''' devuelve una linea (array) de a0 a a1 en longitud t'''
        return np.linspace(a0, a1, _t)

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