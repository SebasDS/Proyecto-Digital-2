#from scipy.io import wavfile
from migen import *
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
    def __init__(self, sample_freq, scl):
        self.fil_clock = fil_clock = Signal()
        self.counter = counter = Signal(12)
        self.fil_rate = fil_rate = Signal(23)
        self.clk_por_period = clk_por_period = Signal(5)


        self.sync += [counter.eq(counter+1)]

        self.comb += [
            fil_rate.eq(128*sample_freq),
            #If(fil_rate == 5644800, # Caso para 16 bits a frecuencia de 44100 Hz
            clk_por_period.eq(9),
            #),
            fil_clock.eq(counter < clk_por_period),
            scl.eq(fil_clock)
        ]

        self.sync +=[
            If(counter == clk_por_period*2-1,
                counter.eq(0)
            ),
        ]


class BitClock(Module, AutoCSR):
    def __init__(self, sample_freq, width_word, bck):
        self.bit_clock = bit_clock = Signal()
        self.counter = counter = Signal(12)
        self.bit_rate = bit_rate = Signal(23)
        self.clk_por_bit = clk_por_bit = Signal(12)
        self.fl_up_bck = fl_up_bck = Signal()
        self.fl_down_bck = fl_down_bck = Signal()


        self.sync += [counter.eq(counter+1)]

        self.comb += [
            bit_rate.eq(2*width_word*sample_freq),
            #If(bit_rate == 1411200, # Caso para 16 bits a frecuencia de 44100 Hz
            clk_por_bit.eq(36),
            #),
            fl_up_bck.eq(counter == 69),
            fl_down_bck.eq(counter == 34),
            bit_clock.eq(counter < clk_por_bit),
            bck.eq(bit_clock)
        ]
        #     #bit_clock.eq(counter < clk_por_bit)
        #     If(counter == clk_por_bit*2,
        #         counter.eq(0)
        #     ).Else(
        #         If(counter < clk_por_bit,
        #             bit_clock.eq(1)
        #         ).Else(
        #             bit_clock.eq(0)
        #         )
        #     )
        # ]
        self.sync +=[
            If(counter == clk_por_bit*2-1,
                    counter.eq(0)
                ),#.Else(
                #    If(counter < clk_por_bit,
                #        bit_clock.eq(1)
                #    ).Else(
                #        bit_clock.eq(0)
                #    )
                #),

        ]

class WordSelector(Module, AutoCSR):
    def __init__(self, word_width, flanco_bajada, lck):
        self.channel = channel = Signal()
        self.counter = counter = Signal(7)
        self.bit_reset = bit_reset = Signal(3)
        self.fl_ws_up = fl_ws_up = Signal()
        self.fl_ws_down = fl_ws_down = Signal()
        self.fl_bits_up = fl_bits_up = Signal()
        self.fl_bits_down = fl_bits_down = Signal()

        self.comb += [
            #If(word_width == 16,
            #    br=5
                #bit_reset.eq(5) #Caso para word_width = 16 bits
            #).Else(
            #    br=6
                #bit_reset.eq(6) #Caso para word_width = 32 bits
            #),
            fl_ws_down.eq(flanco_bajada & (counter == 31)),
            fl_ws_up.eq(flanco_bajada & (counter ==15)),
            fl_bits_down.eq(flanco_bajada & (counter == 0)),
            fl_bits_up.eq(flanco_bajada & (counter ==16)),

            channel.eq(counter[4]),
            lck.eq(channel)
        ]

        self.sync += [
            #If(flanco_bajada == 1,
            #    counter.eq(counter+1)
            #),
            counter.eq(counter+flanco_bajada),
            If(counter[5] == 1,
                counter.eq(0)
            )
        ]


#class Serializacion(Module, AutoCSR):
#    def __init__(self):

class _I2S(Module, AutoCSR):
    def __init__(self, flt, dmp, scl, bck, din, lck, fmt, xmt):                                              # flt, dmp, scl, bck, din, lck, fmt, xmt):
        self.Width_word = Width_word = Signal(32)
        self.Sample_Frecuency  = Sample_Frecuency = Signal(32)
        #self.Number_channels = Number_channels = Signal() # 0=mono, 1=estereo
        self.Swap = Swap = Signal() #0=Direccion par al canal izquierdo, 1=Direccion par al canal derecho
        #self.Enable_txrx = Enable_txrx = Signal() # 0=Transmision, 1=Recepcion
        self.data_left = data_left = Signal(16)
        self.data_right = data_right = Signal(16)
        self.en_left_sw = en_left_sw = Signal()
        self.en_right_sw = en_right_sw = Signal()
        self.en_left = en_left = Signal()
        self.en_right = en_right = Signal()
        self.buffer = buffer = Signal(16)
        self.bit_out = bit_out = Signal()
        self.counter_bits = counter_bits = Signal(5)
        self.counter_muestra = counter_muestra = Signal(6)

        #fs, data = wavefile.read("3A_La_Cucaracha-cvt.wav")
        #print(fs+"\n")
        #print(data)
        cucaracha = open("3A_La_Cucaracha-cvt.wav","r")
        i=0
        dato=[]
        start=True
        cancion={}
        while (1):
            data_LSB = cucaracha.read(1)
            data_MSB = cucaracha.read(1)
            if not data_LSB:
                break
            dato = [ord(data_MSB),ord(data_LSB)]
            cancion[i] = data_left.eq(dato[0]*256+dato[1])
            print(dato)
            i += 1

        cucaracha.close()


        cases = {}
        sinusoidal_400 = {}

        # for i in range(44):
        #     sinusoidal_400[i] = data_left.eq(int(round((math.sin(math.pi*2*1000*i/44100)+1)*16383)))
        #     print (int(round((math.sin(math.pi*2*1000*i/44100)+1)*16383)))

        # # #
        # Submodulo generador de reloj para bits
        self.submodules.bitClock = BitClock(self.Sample_Frecuency, self.Width_word, bck)
        self.submodules.wordSelect = WordSelector(self.Width_word, self.bitClock.fl_down_bck, lck)
        self.submodules.filterClock = FilterClock(self.Sample_Frecuency, scl)
        self.submodules.configuracion = Configuracion(flt, dmp, fmt, xmt)
       # ingrese la lógica respectiva  para el periferico

        for i in range(16):
            cases[i] = din.eq(buffer[15-i])

        self.sync += [
            counter_bits.eq(counter_bits+self.bitClock.fl_down_bck),
            counter_muestra.eq(counter_muestra+en_left_sw),
            #If(counter_bits[4] == 1,
            #    counter_bits.eq(0)
            #),
            en_left_sw.eq((~Swap & self.wordSelect.fl_ws_up) | (Swap & self.wordSelect.fl_ws_down)),
            en_right_sw.eq((~Swap & self.wordSelect.fl_ws_down) | (Swap & self.wordSelect.fl_ws_up)),

            en_left.eq((~Swap & self.wordSelect.fl_bits_up) | (Swap & self.wordSelect.fl_bits_down)),
            en_right.eq((~Swap & self.wordSelect.fl_bits_down) | (Swap & self.wordSelect.fl_bits_up)),

            If(en_left,
                counter_bits.eq(0),
                buffer.eq(data_left)
            ).Elif(en_right,
                counter_bits.eq(0),
                buffer.eq(data_right)
            ),

            If((counter_muestra == len(cancion)) & en_left_sw,
                counter_muestra.eq(0)
            ),

        ]



        self.comb += [
            Swap.eq(0),
            #data_left.eq(10986),
            #data_right.eq(63669),
            #bit_out.eq(buffer[15-self.wordSelect.counter])
            If(self.wordSelect.channel,
                Case(counter_muestra,cancion)
                ),
            Case(counter_bits, cases)
        ]





class I2S(Module, AutoCSR):
    def __init__(self, flt, dmp, scl, bck, din, lck, fmt, xmt):                                    #flt, dmp, scl, bck, din, lck, fmt, xmt):
        self.Width_word = CSRStorage(32)
        self.Sample_Frecuency = CSRStorage(32)
        #self.Number_channels = CSRStorage()
        self.Swap = CSRStorage()
        #self.Enable_txrx = CSRStorage()
        self.En_left = CSRStatus()
        self.En_right = CSRStatus()
        self.data_left = CSRStorage(16)
        self.data_right = CSRStorage(16)

        # # #

        #self.submodules.ev = EventManager()
        #self.ev.zero = EventSourcePulse()
        #self.ev.finalize()

        _i2s = _I2S(flt, dmp, scl, bck, din, lck, fmt, xmt)                                            #flt, dmp, scl, bck, din, lck, fmt, xmt)
        self.submodules += _i2s

        self.comb += [
           _i2s.Width_word.eq(self.Width_word.storage),
           _i2s.Sample_Frecuency.eq(self.Sample_Frecuency.storage),
         #  _i2s.Number_channels.eq(self.Number_channels.storage),
           _i2s.Swap.eq(self.Swap.storage),
           #_i2s.Enable_txrx.eq(self.Enable_txrx.storage),
           _i2s.data_left.eq(self.data_left.storage),
           _i2s.data_right.eq(self.data_right.storage),
           self.En_left.status.eq(_i2s.en_left_sw),
           self.En_right.status.eq(_i2s.en_right_sw),
        ]

if __name__ == '__main__':
    bck = Signal()
    lck = Signal()
    din = Signal()
    scl = Signal()
    flt = Signal()
    dmp = Signal()
    fmt = Signal()
    xmt = Signal()
    dut = _I2S(flt, dmp, scl, bck, din, lck, fmt, xmt)

    def dut_tb(dut):
        yield dut.Width_word.eq(16)
        yield dut.Sample_Frecuency.eq(44100)
        for i in range(10000):
        	yield

    run_simulation(dut, dut_tb(dut), vcd_name="i2s.vcd")
