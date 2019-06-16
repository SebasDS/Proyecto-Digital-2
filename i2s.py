from migen import *

from litex.soc.interconnect.csr import *

# @FABELTRANM  unal 2019
# Modulo ejemplo para crear perifericos conectados con wishbone
# Recuerde:
#     CSRStorage: permite leer  y escribir en el Registro del periferico desde el procesador
#     CSRStatus:  Unicamente leer el valor dle Reg
#     la comunicación del software  con el peroférico se facilita conel archivo csr.h


class _I2S(Module, AutoCSR):
    def __init__(self, din, ws, bck):
        self.Resolution = Resolution = Signal(32)
        self.Bit_rate  = Bit_rate = Signal(32)
        self.Number_channels = Number_channels = Signal() # 0=mono, 1=estereo
        self.Swap = Swap = Signal() #0=Direccion par al canal izquierdo, 1=Direccion par al canal derecho
        self.Enable_txrx = Enable_txrx = Signal() # 0=Transmision, 1=Recepcion
        self.data = data = Signal(32)

        self.submodules.ev = EventManager()
        self.ev.higher_tx = EventSourcePulse()
        self.ev.higher_rx = EventSourcePulse()
        self.ev.lower_tx = EventSourcePulse()
        self.ev.lower_rx = EventSourcePulse()
        self.ev.finalize()

        # # #

       # ingrese la lógica respectiva  para el periferico
        self.sync += [


        ]

        self.comb += [

        ]





class I2S(Module, AutoCSR):
    def __init__(self, din, ws, bck):
        self.Resolution = CSRStorage(32)
        self.Bit_rate  = CSRStorage(32)
        self.Number_channels = CSRStorage()
        self.Swap = CSRStorage()
        self.Enable_txrx = CSRStorage()
        self.data = CSRStorage(32)

        # # #

        _i2s = _I2S(din, ws, bck)
        self.submodules += _i2s

        self.comb += [
           _i2s.Resolution.eq(self.Resolution.storage),
           _i2s.Bit_rate.eq(self.Bit_rate.status),
           _i2s.Number_channels.eq(self.Number_channels.storage),
           _i2s.Swap.eq(self.Swap.status),
           _i2s.Enable_txrx.eq(self.Enable_txrx.storage),
           _i2s.data.eq(self.data.storage)
        ]
