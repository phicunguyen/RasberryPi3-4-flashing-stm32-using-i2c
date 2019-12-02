# RasberryPi3-4-flashing-stm32-using-i2c
This python script is used to update the stm32 firmware using i2c. 

If the st-link or jtag is not available on your system to program the stm32 then using i2c or uart is the only choice.
You can also use DFU over usb to program the stm32 but in our case only ethernet is available to access the Raspberry pi.
And the stm32 i2c is also connect to the Raspberry Pi:

  Here is the pin out:
  
         stm32               Raspberry Pi
       i2c1-PB6 (scl)        GPIO3 (scl1)
       i2c1-PB9 (sda)        GPIO2 (sda1)
       
  This project has two python files and the stm32 i2c document:
    
      1. stm32_i2c.py                    (i2c protocol to program the stm32)
      2. stm32_flash.py                  (Using smbus and i2c_msg to write/read the i2c)
      3. i2c_protocol_en.DM00072315.pdf (i2c protocol).
      
  How to run:
  
      python stm32_flash.py firmware.bin (your stm32 firmware binary file).
      
  Run the below commands if your system has not set up for i2c.
  
    sudo apt-get update
    sudo apt-get install python-smbus python-smbus python-dev python-dev i2c-tools
    
    pip install smbus2
