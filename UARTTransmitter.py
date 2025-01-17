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
			tx_reg.next = intbv((1 << 9 ) | (int(data) << 1 )| 0)[10:]
			bit_count.next = 0
			busy.next = True
			
		elif busy and baudrate_clk:
			if bit_count < 10:
				tx.next = tx_reg[0] #LSB first
				tx_reg.next = tx_reg >> 1 #Shift data
				bit_count.next = bit_count + 1
			else:
				busy.next = False # End of transmission
			
	return logic
