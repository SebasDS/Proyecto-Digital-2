from migen import *
from migen.genlib.io import CRG

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform

import litex.soc.integration.soc_core as SC
from litex.soc.integration.builder import *

from litex.soc.cores import gpio
from litex.soc.cores import spi
from i2s import I2S
# platform
#

_io = [
    ("clk32", 0, Pins("E3"), IOStandard("LVCMOS33")),

    ("cpu_reset", 0, Pins("C12"), IOStandard("LVCMOS33")),

    ("serial", 0,
        Subsignal("tx", Pins("D4")),
        Subsignal("rx", Pins("C4")),
        IOStandard("LVCMOS33"),
    ),

    ("i2s_FLT", 0, Pins("B13"), IOStandard("LVCMOS33")),
    ("i2s_DMP", 0, Pins("F14"), IOStandard("LVCMOS33")),
    ("i2s_SCL", 0, Pins("D17"), IOStandard("LVCMOS33")),
    ("i2s_BCK", 0, Pins("E17"), IOStandard("LVCMOS33")),
    ("i2s_DIN", 0, Pins("G13"), IOStandard("LVCMOS33")),
    ("i2s_LCK", 0, Pins("C17"), IOStandard("LVCMOS33")),
    ("i2s_FMT", 0, Pins("D18"), IOStandard("LVCMOS33")),
    ("i2s_XMT", 0, Pins("E18"), IOStandard("LVCMOS33"))

]


class Platform(XilinxPlatform):
    default_clk_name = "clk32"
    default_clk_period = 10

    def __init__(self):
#        XilinxPlatform.__init__(self, "xc6slx9-TQG144-2", _io, toolchain="ise")
        XilinxPlatform.__init__(self, "xc7a100t-CSG324-1", _io, toolchain="ise")

    def do_finalize(self, fragment):
        XilinxPlatform.do_finalize(self, fragment)



#
# design
#

# create our platform (fpga interface)
platform = Platform()

# create our soc (fpga description)
class BaseSoC(SC.SoCCore):
    # Peripherals CSR declaration
    csr_peripherals = {
      #"spiLCD":2,
      #"spiSD":3,
      #"GPIO":4,
      "i2s":2
      #"i2c":6
    }
    SC.SoCCore.csr_map=csr_peripherals
    # interrupts declaration
    #interrupt_map = {
    #    "i2s" : 4
    #}
    #SC.SoCCore.interrupt_map=interrupt_map
    print (SC.SoCCore.csr_map)
    def __init__(self, platform):
        sys_clk_freq = int(100e6)
        # SoC with CPU
        SC.SoCCore.__init__(self, platform,
            cpu_type="lm32",
            clk_freq=100e6,
            ident="ReproductorWAV", ident_version=True,
            integrated_rom_size=0x8000,
            integrated_main_ram_size=16*1024)

        # Clock Reset Generation
        self.submodules.crg = CRG(platform.request("clk32"), ~platform.request("cpu_reset"))
        # Modulos
        self.submodules.i2s = I2S(
        #    platform.request("i2s_FLT"),
        #    platform.request("i2s_DMP"),
            platform.request("i2s_SCL"),
            platform.request("i2s_BCK"),
        #    platform.request("i2s_DIN"),
            platform.request("i2s_LCK")
        #    platform.request("i2s_FMT"),
        #    platform.request("i2s_XMT")
        )


        print (SC.SoCCore.interrupt_map)

soc = BaseSoC(platform)




#
# build
#

builder = Builder(soc, output_dir="build", csr_csv="test/csr.csv")
builder.build()
