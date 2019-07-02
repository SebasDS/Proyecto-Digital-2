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
        self.comb += bck.eq(counter > cyc_lvl)

class WordSelector(Module, AutoCSR):
    def __init__(self, counter, bit_word, ws):
        self.comb += ws.eq(counter >= bit_word)

class _I2S(Module, AutoCSR):
    def __init__(self, flt, dmp, scl, bck, sd, ws, fmt, xmt):                                             # flt, dmp, scl, bck, din, lck, fmt, xmt):

##############################################################################################################
        self.width_word = width_word = Signal(6)
        self.divisor_bck = divisor_bck = Signal(7)
        self.divisor_scl = divisor_scl = Signal(5)
        self.start = start = Signal()
        self.counter_bck = counter_bck = Signal(7)
        self.counter_scl = counter_scl = Signal(5)
        self.counter_ws = counter_ws = Signal(5)
        self.counter_word = counter_word = Signal(5)
        self.load_buffer = load_buffer = Signal()
        self.load_bit = load_bit = Signal()
        self.load_muestreo = load_muestreo = Signal()
        self.data_left = data_left = Signal(32)
        self.data_right = data_right = Signal(32)
        self.buffer = buffer = Signal(32)
        self.channel = channel = Signal()
        self.j = j = Signal(6)
        # ingrese la lógica respectiva  para el periferico


        sinusoidal_1000 = {}
        for i in range(44):
            sinusoidal_1000[i] =data_left.eq(int(round((math.sin(math.pi*2*1000*i/44100)+1)*16383)))
            print (int(round((math.sin(math.pi*2*1000*i/44100)+1)*16383)))



        #########################################################################################
        self.comb += [

            width_word.eq(16),
            divisor_bck.eq(35),
            divisor_scl.eq(9),

            load_bit.eq(counter_bck == divisor_bck*2-1),
            load_buffer.eq(counter_word == width_word),
            load_muestreo.eq((counter_ws == width_word*2-1) & load_bit),
            channel.eq(counter_ws >= width_word),

            If(~self.channel,
                Case(j,sinusoidal_1000)
            )
        ]
        #########################################################################################
        self.sync += [
            # Contador para Reloj de datos
            counter_bck.eq(counter_bck+1),
            If(counter_bck == divisor_bck*2-1,
                counter_bck.eq(0)
            ),

            # Contador para Reloj de Filtro
            counter_scl.eq(counter_scl+1),
            If(counter_scl == divisor_scl*2-1,
                counter_scl.eq(0)
            ),
            #Contador de Muestreo
            j.eq(j+load_muestreo),
            If(j == 44,
                j.eq(0)
            )
        ]
        ########################################################################################3
        self.submodules.i2s_fsm = FSM(reset_state="IDLE")
        self.i2s_fsm.act("IDLE",
            #If(start,
                NextState("RESET_CLOCKS")
            #)
        )

        self.i2s_fsm.act("RESET_CLOCKS",
            NextValue(counter_bck, 0),
            NextValue(counter_scl, 0),
            NextValue(counter_ws, 0),
            NextState("LOAD")
        )
        self.i2s_fsm.act("SERIALIZAR",
            If(load_bit,
                If(width_word == 16,
                    NextValue(sd, buffer[15]),
                    NextValue(buffer, Cat(0,buffer[0:30]))
                    #sd.eq(Mux(counter_word,buffer[15],buffer[15],buffer[15],buffer[12],buffer[11],buffer[10],buffer[9],buffer[8],buffer[7],buffer[6],buffer[5],buffer[4],buffer[3],buffer[2],buffer[1],buffer[0]))
                ).Elif(width_word == 32,
                    NextValue(sd, buffer[31]),
                    NextValue(buffer, Cat(0,buffer[0:30]))
                    #sd.eq(Mux(counter_word,buffer[31]))
                ),#.Else(
                #    print("Error en el tamaño de bits")
                #),
                NextValue(counter_word,counter_word+1),
                NextValue(counter_ws,counter_ws+1)

            ),
            If(load_buffer,
                NextState("LOAD")
            )
        )
        self.i2s_fsm.act("LOAD",
            #If(channel,
            #    NextValue(buffer, data_right),
            #).Else(
            #    NextValue(buffer, data_left)
            #),
            NextValue(buffer,Mux(channel, data_right, data_left)),
            NextValue(counter_word, 0),
            NextState("SERIALIZAR")
        )
        ##########################################################################################3
        self.submodules.bitClock = BitClock(counter_bck, divisor_bck, bck)
        self.submodules.filClock = FilterClock(counter_scl, divisor_scl, scl)
        self.submodules.wordSelect = WordSelector(counter_ws, width_word, ws)
        self.submodules.configuracion = Configuracion(flt, dmp, fmt, xmt)


class I2S(Module, AutoCSR):
    def __init__(self, flt, dmp, scl, bck, sd, ws, fmt, xmt):                                    #flt, dmp, scl, bck, din, lck, fmt, xmt):
        self.Width_word = CSRStorage(32)
        self.Divisor_BCK = CSRStorage(7)
        self.Divisor_SCL = CSRStorage(5)
        #self.En_left = CSRStatus()
        #self.En_right = CSRStatus()
        self.data_left = CSRStorage(32)
        self.data_right = CSRStorage(32)
        self.Start = CSRStorage()

        # # #

        #self.submodules.ev = EventManager()
        #self.ev.zero = EventSourcePulse()
        #self.ev.finalize()

        _i2s = _I2S(flt, dmp, scl, bck, sd, ws, fmt, xmt)                                            #flt, dmp, scl, bck, din, lck, fmt, xmt)
        self.submodules += _i2s

        self.comb += [
           _i2s.width_word.eq(self.Width_word.storage),
           _i2s.divisor_bck.eq(self.Divisor_BCK.storage),
           _i2s.divisor_scl.eq(self.Divisor_SCL.storage),
           _i2s.start.eq(self.Start.storage),
           _i2s.data_left.eq(self.data_left.storage),
           _i2s.data_right.eq(self.data_right.storage),
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
    dut = _I2S(flt, dmp, scl, bck, sd, ws, fmt, xmt)

    def dut_tb(dut):
        #yield dut.data_left.eq(10986)
        #yield dut.data_right.eq(30901)
        yield dut.width_word.eq(16)
        yield dut.divisor_bck.eq(35)
        yield dut.divisor_scl.eq(9)
        #yield dut.start.eq(1)
        for i in range(10000):
        	yield

    run_simulation(dut, dut_tb(dut), vcd_name="i2s.vcd")
