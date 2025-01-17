from myhdl import block, always, always_seq, Signal, intbv, instance, delay, StopSimulation, concat

@block
def BaudRateGenerator(baudrate_clk, clk, divisor):
    count = Signal(intbv(0, min=0, max=divisor))
    
    @always(clk.posedge)
    def logic():
        if count == divisor - 1:
            count.next = 0
            baudrate_clk.next = not baudrate_clk
        else:
            count.next = count + 1
    
    return logic
