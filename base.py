from migen import *
from migen.genlib.io import CRG

from litex.build.generic_platform import *
from litex.build.xilinx import XilinxPlatform

import litex.soc.integration.soc_core as SC
from litex.soc.integration.builder import *

from litex.soc.cores import gpio
from litex.soc.cores import spi
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
      "spiLCD":2,
      "spiSD":3,
      "GPIO":4,
      "i2s":5,
      "i2c":6,
    }
    SC.SoCCore.csr_map=csr_peripherals
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
        # interrupts declaration
        interrupt_map = {
            "i2s" : 4
        }
        SC.SoCCore.interrupt_map.update(interrupt_map)
        print (SC.SoCCore.interrupt_map)

soc = BaseSoC(platform)




#
# build
#

builder = Builder(soc, output_dir="build", csr_csv="test/csr.csv")
builder.build()
