"""UART hardware design written in myhdl"""

from myhdl import block, always_seq,Signal, intbv,always,instance,delay,ResetSignal, StopSimulation
from UARTTransmitter import UARTTransmitter
from UARTReceiver import UARTReceiver
from BaudRateGenerator import BaudRateGenerator

@block
def testbench():
	clk = Signal(bool(0))
	baudrate_clk = Signal(bool(0))
	tx = Signal(bool(1))
	rx = Signal(bool(1))
	data_tx = Signal(intbv(0x5A)[8:])
	data_rx = Signal(intbv(0)[8:])
	start = Signal(bool(0))
	valid = Signal(bool(0))
	busy = Signal(bool(0))
	baud_divisor = 16 # Assuming 16 clock cycles per baud period
	
	#Instantiate UART modules
	baud_gen = BaudRateGenerator(baudrate_clk, clk, baud_divisor)
	transmitter = UARTTransmitter(tx, data_tx, start, clk, baudrate_clk, busy)
	receiver = UARTReceiver(rx, data_rx, valid,clk, baudrate_clk)
	
	#Connect Tx to Rx for loop feedback
	@always(delay(1))
	def loopback():
		rx.next = tx
		
	#Clock generation
	@always(delay(5))
	def clkgen():
		clk.next = not clk
		
	#Stimulus
	@instance
	def stimulus():
		print("Starting UART Test...")
		yield delay(20)
		
		#Transmit data
		print(f"Sending data: {hex(data_tx)}")
		start.next = True
		yield clk.posedge
		start.next = False
		
		#Wait for transmission to complete
		while busy:
			yield clk.posedge
			
		#Wait for receiver to  validate data
		while not valid:
			yield clk.posedge
			
		print(f"Received data: {hex(data_rx)}")
		assert data_tx == data_rx, "Data mismatch!"
		
		print("UART Test Passed")
		raise StopSimulation
		
	return baud_gen, transmitter, receiver, loopback, clkgen, stimulus
	
#Run the testbench
UART_tb = testbench()
UART_tb.config_sim(trace=True)
UART_tb.run_sim()
