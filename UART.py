"""UART hardware design written in myhdl"""

from myhdl import block, always_seq,Signal, intbv,always,instance,delay,ResetSignal, StopSimulation

@block
def UARTTransmitter(tx, data, start, clk, baudrate_clk, busy):
	"""
	UART Transmitter
	
	tx		-- Transmitted data (serial output)
	data		-- Data to transmit (8 bits)
	start		-- Start trasmission signal
	clk		-- System clock
	baudrate_clk 	-- Baud rate clock enable
	busy		-- Transmisssion busy indicator
	"""
	
	tx_reg = Signal(intbv(0)[10:]) # Start bit + 8 data bits + Stop bits
	bit_count = Signal(intbv(0,min=0,max = 11)) #Track trasmitted bits
	
	@always_seq(clk.posedge, reset=None)
	def logic():
		if start and not busy:
			# Load start bit (0), data, and stop bit(1) into tx_reg
			tx_reg.next = concat(Signal(intbv(1)[1:]),data,Signal(intbv(0)[1:]))
			bit_count.next = 0
			busy.next = True
			
		elif busy and baudrate_clk:
			if bit_count < 10:
				tx.next = tx_reg[0] #LSB first
				tx_reg.next = tx_reg >> 1 #Shift data
				bit_count = bit_count + 1
			else:
			busy.next = False # End of transmission
			
	return logic
	
@block
def UARTReceiver(rx, data, valid,clk, baudrate_clk):
	"""
	UART Receiver
	
	rx	-- Received data (serial input)
	data	-- Received data (8 bits)
	valid	-- Valid data signal
	clk	-- System clock
	baudrate_clk	-- Baud rate clock enable
	"""
	
	rx_reg = Signal(intbv(0)[10:]) 
	bit_count = Signal(intbv(0,min=0,max=11)) # Tracks received bits
	receiving = Signal(bool(0))
	
	@always_seq(clk.posedge, reset=None)
	def logic():
		if not receiving and rx == 0:
			receiving.next = True
			bit_count.next = 0
		
		elif receiving and baudrate_clk:
			if bit_count < 10:
				rx_reg.next = concat(rx,rx_reg[9:1])
				bit_count.next = bit_count + 1
			else:
				# Data received, extract 8 bits and validate stop bit
				if rx_reg[9]:	# Stop bit must be 1
					data.next = rx_reg[8:0]
					valid.next = True
				receiving.next = False
				valid.next = False
				
	return logic
	
@block
def BaudRateGenerator(baurate_clk, clk, baud_divisor):
	"""
	Baud Rate Generator
	
	baudrate_clk	-- Baudrate clock enable
	clk		-- System clock
	baud_divisor	-- Baudrate divisor
	"""
	
	counter = Signal(intbv(0,min=0,max=baud_divisor))
	
	@always_seq(clk.posedge, reset=None)
	def logic():
		if counter == baud_divisor -1:
			baudrate_clk.next = True
			counter.next = 0
		else:
			baudrate_clk.next = False
			counter.next = counter + 1
			
	return logic
	

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
tb.run_sim()
