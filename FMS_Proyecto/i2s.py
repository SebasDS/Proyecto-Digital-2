from migen import *
from migen.genlib.fsm import *
import math
from litex.soc.interconnect.csr import *
from litex.soc.interconnect.csr_eventmanager import *
# @FABELTRANM  unal 2019
# Modulo ejemplo para crear perifericos conectados con wishbone
# Recuerde:
#     CSRStorage: permite leer  y escribir en el Registro del periferico desde el procesador
#     CSRStatus:  Unicamente leer el valor dle Reg
#     la comunicación del software  con el peroférico se facilita conel archivo csr.h
class Configuracion(Module, AutoCSR):
    def __init__(self, flt, dmp, fmt, xmt):
        self.comb += [
            flt.eq(0),
            dmp.eq(0),
            fmt.eq(0),
            xmt.eq(1)
        ]

class FilterClock(Module, AutoCSR):
    def __init__(self, counter, cyc_lvl, scl):
        self.comb += scl.eq(counter < cyc_lvl)

class BitClock(Module, AutoCSR):
    def __init__(self, counter, cyc_lvl, bck):
        self.comb += bck.eq(counter < cyc_lvl)

class WordSelector(Module, AutoCSR):
    def __init__(self, counter, bit_word, sd):
        self.comb += lck.eq(counter < bit_word)

class _I2S(Module, AutoCSR):
    def __init__(self, flt, dmp, scl, bck, sd, ws, fmt, xmt, clk_freq):                                             # flt, dmp, scl, bck, din, lck, fmt, xmt):
        # sinusoidal_400 = {}
        # for i in range(44):
        #     sinusoidal_400[i] = data_left.eq(int(round((math.sin(math.pi*2*1000*i/44100)+1)*16383)))#, data_right.eq(int(round(math.sin(i/44100)*32767))))
        #     print (int(round((math.sin(math.pi*2*1000*i/44100)+1)*16383)))
##############################################################################################################
        self.width_word = width_word = Signal(6)
        self.sample_frecuency = sample_frecuency = Signal(16)
        self.start = start = Signal()
        self.counter_bck = counter_bck = Signal(7)
        self.counter_scl = counter_scl = Signal(5)
        self.counter_word = counter_word = Signal(6)
        self.load_buffer = load_buffer = Signal()
        self.load_bit = load_bit = Signal()
        self.data_left = data_left = Signal(32)
        self.data_right = data_right = Signal(32)
        self.buffer = buffer = Signal(32)
        self.clk_bck = clk_bck = Signal(7)
        self.clk_scl = clk_scl = Signal(5)

        # ingrese la lógica respectiva  para el periferico
        #########################################################################################
        self.comb += [
            load_bit.eq(counter_bck == clk_bck-1),
            load_buffer.eq((counter_word == width_word) | (counter_word == width_word*2))
        ]
        #########################################################################################
        self.sync += [
            # Contador para Reloj de datos
            counter_bck.eq(counter_bck+1),
            If(counter_bck == clk_bck-1,
                counter_bck.eq(0)
            ),

            # Contador para Reloj de Filtro
            counter_scl.eq(counter_scl+1),
            If(counter_scl == clk_scl-1,
                counter_scl.eq(0)
            )
        ]
        ########################################################################################3
        self.submodules.i2s_fsm = FSM(reset_state="IDLE")
        self.i2s_fsm.act("IDLE",
            If(start,
                NextState("CONFIG")
            )
        )
        self.i2s_fsm.act("CONFIG",
            If(width_word == 16,
                If(sample_frecuency == 48000,
                    NextValue(clk_bck, 66),
                    NextValue(clk_scl, 16),
                    NextState("CLOCKS")
                ).Elif(sample_frecuency == 44100,
                    NextValue(clk_bck, 70),
                    NextValue(clk_scl, 18),
                    NextState("CLOCKS")
                )
            ).Elif(width_word == 32,
                If(sample_frecuency == 48000,
                    NextValue(clk_bck, 32),
                    NextValue(clk_scl, 16),
                    NextState("CLOCKS")
                ).Elif(sample_frecuency == 44100,
                    NextValue(clk_bck, 36),
                    NextValue(clk_scl, 18),
                    NextState("CLOCKS")
                )
            )
        )
        self.i2s_fsm.act("CLOCKS",
            NextValue(counter_bck, 0),
            NextValue(counter_scl, 0),
            NextValue(counter_word, 0),
            NextState("LOAD")
        )
        self.i2s_fsm.act("DATOS",
            If(load_bit,
                If(width_word == 16,
                    NextValue(sd, buffer[15]),
                    NextValue(buffer, Cat(buffer[30:0],0))
                    #sd.eq(Mux(counter_word,buffer[15],buffer[15],buffer[15],buffer[12],buffer[11],buffer[10],buffer[9],buffer[8],buffer[7],buffer[6],buffer[5],buffer[4],buffer[3],buffer[2],buffer[1],buffer[0]))
                ).Elif(width_word == 32,
                    NextValue(sd, buffer[31]),
                    NextValue(buffer, Cat(buffer[30:0],0))
                    #sd.eq(Mux(counter_word,buffer[31]))
                ).Else(
                    print("Error en el tamaño de bits")
                ),
                NextValue(counter_word,counter_word+1),
                
            ),
            If(load_buffer,
                    NextState("LOAD")
            ),
        ),
        self.i2s_fsm.act("LOAD",
            If(counter_word[4], #Para el caso de width_word = 16
                NextValue(buffer, data_right),
            ).Else(
                NextValue(buffer, data_left)
            ),
            NextState("DATOS")
        )
        ##########################################################################################3
        self.submodules.bitClock = BitClock(counter_bck, 35, bck)
        self.submodules.filClock = FilterClock(counter_scl, 9, scl)



class I2S(Module, AutoCSR):
    def __init__(self, flt, dmp, scl, bck, sd, ws, fmt, xmt, clk_freq):                                    #flt, dmp, scl, bck, din, lck, fmt, xmt):
        self.Width_word = CSRStorage(32)
        self.Sample_Frecuency = CSRStorage(32)
        self.En_left = CSRStatus()
        self.En_right = CSRStatus()
        self.data_left = CSRStorage(16)
        self.data_right = CSRStorage(16)
        self.Start = CSRStorage()

        # # #

        #self.submodules.ev = EventManager()
        #self.ev.zero = EventSourcePulse()
        #self.ev.finalize()

        _i2s = _I2S(flt, dmp, scl, bck, sd, ws, fmt, xmt, clk_freq)                                            #flt, dmp, scl, bck, din, lck, fmt, xmt)
        self.submodules += _i2s

        self.comb += [
           _i2s.width_word.eq(self.Width_word.storage),
           _i2s.sample_frecuency.eq(self.Sample_Frecuency.storage),
           _i2s.start.eq(self.Start.storage)
           #_i2s.data_left.eq(self.data_left.storage),
           #_i2s.data_right.eq(self.data_right.storage),
           #self.En_left.status.eq(_i2s.en_left_sw),
           #self.En_right.status.eq(_i2s.en_right_sw),
        ]

if __name__ == '__main__':
    bck = Signal()
    ws = Signal()
    sd = Signal()
    scl = Signal()
    flt = Signal()
    dmp = Signal()
    fmt = Signal()
    xmt = Signal()
    dut = _I2S(flt, dmp, scl, bck, sd, ws, fmt, xmt, 100000000)

    def dut_tb(dut):
        yield dut.width_word.eq(16)
        yield dut.sample_frecuency.eq(44100)
        for i in range(10000):
        	yield

    run_simulation(dut, dut_tb(dut), vcd_name="i2s.vcd")
