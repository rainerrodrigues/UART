from myhdl import block, always, always_seq, Signal, intbv, instance, delay, StopSimulation, concat

@block
def UARTReceiver(rx, data, valid, clk, baudrate_clk):
    shift_reg = Signal(intbv(0)[8:])
    bit_count = Signal(intbv(0, min=0, max=10))
    receiving = Signal(bool(0))
    
    @always_seq(clk.posedge, reset=None)
    def logic():
        if not receiving and not rx:  # Start bit detection
            receiving.next = True
            bit_count.next = 0
            valid.next = False
        elif receiving and baudrate_clk:
            if bit_count < 8:
                shift_reg.next = concat(rx, shift_reg[8:1])
                bit_count.next = bit_count + 1
            elif bit_count == 8:  # Stop bit validation
                if rx:  # Check stop bit
                    data.next = shift_reg
                    valid.next = True
                receiving.next = False
    return logic
