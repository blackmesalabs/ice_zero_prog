##############################################################################
# ice_zero_prog.py
#             Copyright (c) Kevin M. Hubbard 2017 BlackMesaLabs
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Description:
#   This uses GPIO pins on a RaspPi to bit-bang SPI protocol to a FPGA PROM.
#
# Revision History:
# Ver   When       Who       What
# ----  --------   --------  ---------------------------------------------------
# 0.01  2017.01.22 khubbard  Creation. Reads PROM ID.
#
##############################################################################
import sys;
import RPi.GPIO as GPIO;

class App:
  def __init__(self):
    return;

  def main(self):
    self.main_init();
#   self.main_loop();

  def main_init( self ):
    args = sys.argv + [None]*5;# args[0] is this scripts name
    self.arg0     = args[1];
    self.arg1     = args[2];
    self.spi_link = spi_link( platform="ice_zero_proto" );
#   miso_bytes = self.spi_link.xfer( [0xAB],  0 );# Wake from deep sleep
    miso_bytes = self.spi_link.xfer( [0x9F], 17 );# Micron READ_ID
    for each in miso_bytes:
      print("%02x" % ( each ) );
    self.spi_link.close();
    return;

  def main_loop( self ):
    while( True ):
      pass;
    return;


###############################################################################
# Class for bit banging to Micron SPI PROM connected to Lattice ICE40 FPGA
class spi_link:
  def __init__ ( self, platform ):
    try:
      import RPi.GPIO as GPIO;
    except:
      raise RuntimeError("ERROR: Unable to import RaspPi RPi.GPIO module");

    if ( platform == "ice_zero_proto" ):
      GPIO.setmode(GPIO.BOARD);
      self.pin_rst_l = 37;
      self.pin_clk   = 36;
      self.pin_cs_l  = 32;
      self.pin_miso  = 31;
      self.pin_mosi  = 33;
      self.pin_done  = 39;
    else:
      raise RuntimeError("ERROR: Unknown platform " + platform );

    GPIO.setup( self.pin_rst_l, GPIO.OUT, initial = GPIO.LOW );
    GPIO.setup( self.pin_cs_l , GPIO.OUT, initial = GPIO.HIGH );
    GPIO.setup( self.pin_clk  , GPIO.OUT, initial = GPIO.LOW  );
    GPIO.setup( self.pin_mosi , GPIO.OUT, initial = GPIO.LOW  );
    GPIO.setup( self.pin_miso , GPIO.IN                       );
    return;

  def close( self ):
    GPIO.setup( self.pin_cs_l , GPIO.IN );
    GPIO.setup( self.pin_clk  , GPIO.IN );
    GPIO.setup( self.pin_mosi , GPIO.IN );
    GPIO.setup( self.pin_rst_l, GPIO.IN );
    return;

  def xfer( self, mosi_bytes, miso_bytes_len ):
    GPIO.output( self.pin_cs_l , GPIO.LOW);# Assert Chip Select
    miso_bytes = [];
    for each_byte in mosi_bytes:
      shift_reg = each_byte;
      for i in range(0,8,1):
        bit = 0x80 & shift_reg;
        if ( bit == 0x00 ):
          GPIO.output( self.pin_mosi , GPIO.LOW);
        else:
          GPIO.output( self.pin_mosi , GPIO.HIGH);
        GPIO.output( self.pin_clk , GPIO.HIGH);
        GPIO.output( self.pin_clk , GPIO.LOW );
        shift_reg = ( shift_reg << 1 );
    for i in range(0, miso_bytes_len):
      shift_reg = 0x00;
      for i in range(0,8,1):
        bit = GPIO.input( self.pin_miso );
        GPIO.output( self.pin_clk , GPIO.HIGH);
        GPIO.output( self.pin_clk , GPIO.LOW );
        shift_reg = (bit     ) + (shift_reg << 1);
      miso_bytes += [ shift_reg ];   
    GPIO.output( self.pin_cs_l , GPIO.HIGH);# Assert Chip Select
    return miso_bytes;


###############################################################################
app = App();
app.main();
