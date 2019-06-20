from migen import *

from litex.soc.interconnect.csr import *

# @FABELTRANM  unal 2019
# Modulo ejemplo para crear perifericos conectados con wishbone
# Recuerde:
#     CSRStorage: permite leer  y escribir en el Registro del periferico desde el procesador
#     CSRStatus:  Unicamente leer el valor dle Reg
#     la comunicación del software  con el peroférico se facilita conel archivo csr.h
class BitClock(Module, AutoCSR):
    def __init__(self, sample_freq, width_word):
        self.bit_clock = Signal()
        self.counter = Signal(12)
        self.bit_rate = Signal(23)
        self.cyc_clk_bck = Signal(12)


        self.sync += [counter.eq(counter+1)]

        self.comb += [
            bit_rate.eq(2*width_word*sample_freq),
            If(bit_rate == 1411200, # Caso par 16 bits a frecuencia de 44100 Hz
                clk_por_bit.eq(35)
            ),
            #bit_clock.eq(counter < clk_por_bit)
            If(counter == clk_por_bit*2,
                counter.eq(0)
            ).Else(
                If(counter < clk_por_bit,
                    bit_clock.eq(1)
                ).Else(
                    bit_clock.eq(0)
                )
            )
        ]



class _I2S(Module, AutoCSR):
    def __init__(self, flt, dmp, scl, bck, din, lck, fmt, xmt):
        self.Width_word = Width_word = Signal(32)
        self.Sample_Frecuency  = Sample_Frecuency = Signal(32)
        self.Number_channels = Number_channels = Signal() # 0=mono, 1=estereo
        self.Swap = Swap = Signal() #0=Direccion par al canal izquierdo, 1=Direccion par al canal derecho
        self.Enable_txrx = Enable_txrx = Signal() # 0=Transmision, 1=Recepcion
        self.data = data = Signal(self.Width_word)

        #self.submodules.ev = EventManager()
        #self.ev.zero = EventSourcePulse()
        #self.ev.finalize()

        # # #
        # Submodulo generador de reloj para bits
        self.submodules.bitClock = BitClock(self.Sample_Frecuency, self.Width_word)

       # ingrese la lógica respectiva  para el periferico
        #self.sync += [


        #]

        self.comb += [
            bck.eq(bitClock.bit_clock)
        ]





class I2S(Module, AutoCSR):
    def __init__(self, flt, dmp, scl, bck, din, lck, fmt, xmt):
        self.Width_word = CSRStorage(32)
        self.Sample_Frecuency = CSRStorage(32)
        self.Number_channels = CSRStorage()
        self.Swap = CSRStorage()
        self.Enable_txrx = CSRStorage()
        self.data = CSRStorage(Width_word)

        # # #

        _i2s = _I2S(flt, dmp, scl, bck, din, lck, fmt, xmt)
        self.submodules += _i2s

        self.comb += [
           _i2s.Width_word.eq(self.Width_word.storage),
           _i2s.Sample_Frecuency.eq(self.Sample_Frecuency.storage),
           _i2s.Number_channels.eq(self.Number_channels.storage),
           _i2s.Swap.eq(self.Swap.storage),
           _i2s.Enable_txrx.eq(self.Enable_txrx.storage),
           _i2s.data.eq(self.data.storage)
        ]
