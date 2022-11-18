#!/usr/bin/env python
"""
================================================
ABElectronics ADCDAC Pi Analogue to Digital / Digital to Analogue Converter
================================================
Based on the Microchip MCP3202  (new MCP3426)
"""

from __future__ import absolute_import, division, print_function, \
                                                    unicode_literals
#try:
    #import MCP3426
	# pass
#except ImportError:
    #raise ImportError(
        #"MCP3426 not found.")



import smbus
import time

    # Get I2C bus
bus = smbus.SMBus(1)

    # I2C address of the device
MCP3426_DEFAULT_ADDRESS				= 0x68

    # MCP3426 Configuration Command Set
MCP3426_CMD_NEW_CNVRSN				= 0x80 # Initiate a new conversion(One-Shot Conversion mode only)
MCP3426_CMD_CHNL_1					= 0x00 # Channel-1 Selected
MCP3426_CMD_CHNL_2					= 0x20 # Channel-2 Selected
MCP3426_CMD_MODE_CONT				= 0x10 # Continuous Conversion Mode
MCP3426_CMD_MODE_ONESHOT			= 0x00 # One-Shot Conversion Mode
MCP3426_CMD_SPS_240					= 0x00 # 240 SPS (12-bit)
MCP3426_CMD_SPS_60					= 0x04 # 60 SPS (14-bit)
MCP3426_CMD_SPS_15					= 0x08 # 15 SPS (16-bit)
MCP3426_CMD_GAIN_1					= 0x00 # PGA Gain = 1V/V
MCP3426_CMD_GAIN_2					= 0x01 # PGA Gain = 2V/V
MCP3426_CMD_GAIN_4					= 0x02 # PGA Gain = 4V/V
MCP3426_CMD_GAIN_8					= 0x03 # PGA Gain = 8V/V
MCP3426_CMD_READ_CNVRSN				= 0x00 # Read Conversion Result Data


class MCP3426_1():
    
	def config_command(self, channel):
		"""Select the Configuration Command from the given provided values"""
		if channel == 1:
			CONFIG_CMD_1 = (MCP3426_CMD_MODE_CONT | MCP3426_CMD_SPS_240 | MCP3426_CMD_GAIN_1 | MCP3426_CMD_CHNL_1)
			bus.write_byte(MCP3426_DEFAULT_ADDRESS, CONFIG_CMD_1)
		if channel == 2:
			CONFIG_CMD_2 = (MCP3426_CMD_MODE_CONT | MCP3426_CMD_SPS_240 | MCP3426_CMD_GAIN_1 | MCP3426_CMD_CHNL_2)
			bus.write_byte(MCP3426_DEFAULT_ADDRESS, CONFIG_CMD_2)
		
		
	
	def read_adc(self, channel):
		"""Read data back from MCP3426_CMD_READ_CNVRSN(0x00), 2 bytes
		raw_adc MSB, raw_adc LSB"""
		data = bus.read_i2c_block_data(MCP3426_DEFAULT_ADDRESS, MCP3426_CMD_READ_CNVRSN, 2)
		if channel == 1:
				CONFIG_CMD_1 = (MCP3426_CMD_MODE_CONT | MCP3426_CMD_SPS_240 | MCP3426_CMD_GAIN_1 | MCP3426_CMD_CHNL_1)
				bus.write_byte(MCP3426_DEFAULT_ADDRESS, CONFIG_CMD_1)
				raw_adc = ((data[0] & 0x0F) * 256) + data[1]
				if raw_adc > 2047 :
					raw_adc -= 4095

		if channel == 2:
				CONFIG_CMD_2 = (MCP3426_CMD_MODE_CONT | MCP3426_CMD_SPS_240 | MCP3426_CMD_GAIN_1 | MCP3426_CMD_CHNL_2)
				bus.write_byte(MCP3426_DEFAULT_ADDRESS, CONFIG_CMD_2)
				raw_adc = ((data[0] & 0x0F) * 256) + data[1]
				if raw_adc > 2047 :
					raw_adc -= 4095
		    
		# Convert the data to 12-bits
		
		return raw_adc
# from MCP3426 import MCP3426


if __name__ == "__main__":
	mcp3426_1 = MCP3426_1()
	while True :
		mcp3426_1.set_channel()
		mcp3426_1.config_command()
		time.sleep(0.1)
		adc = mcp3426_1.read_adc()
		print ("Digital Value of Analog Input : %d "%(adc['r']))
		print (" ********************************* ")
		time.sleep(0.8)