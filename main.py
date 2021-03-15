from machine import UART, ADC
from time import sleep

# create serial TX
uart = UART(1, baudrate=62500)

# use potentiometer on input pin to change values
adc = ADC()
var_pin = adc.channel(pin='P13')


def sendframe(count=0):

    # steadily increase percentage to simulate changing values
    percent = (frame_count % 100) / 100

    # if count isn't passed, use input pin
    if not frame_count:
        percent = var_pin / 4096
    
    # create frame buffer
    frame = bytearray(33)

    
    frame[0] = 42 # version number
    frame[1] = 84 # PROM
    frame[2] = 1  # status

    ap = percent * 15.2
    MAP = int((ap-1.5) * 18.6)
    frame[3] = MAP  # mass air pressure
    
    wt = percent * 247
    CTS = int((wt+40)/1.125)
    frame[4] = CTS #  coolant temperature

    # frame[5] = IAT

    volts12 = percent * 15.7
    frame[6] = int(volts12*16.24) # system voltage
    volts5 = percent * 4.98
    frame[7] = int(volts5 * 51.2) # sensor voltage

    # max "rpm" is 8000
    rpm = percent * 8000
    
    # convert to milliseconds between spark plug firing
    gap = int(20000000/rpm)

    # break 16-bit value into two bytes
    lowerG = gap & 0xFF
    upperG = (gap >> 8) & 0xFF
    frame[8] = lowerG
    frame[9] = upperG
    print("gap: {} upper: 0x{:02X} lower: 0x{:02X}".format(gap, upperG, lowerG))


    # signal the start of the frame
    uart.write(b'\x00')

    # send each byte of the frame
    for b in frame:

        # if the value is 255, send twice to avoid confusion with endframe marker
        if b == 255:
            uart.write(b'\xFF')
        
        # send frame value
        uart.write(bytes([b]))
    
    # signal the end of the frame
    uart.write(b'\xFF')

# connect TX -> RX to verify sending
def readframe():
    while uart.any():
        raw = uart.read(1)
        print("{}".format(raw))


# manually send frames
sendframe(10)
sendframe(20)


# continually send frame. use frame count to increase values
frame_count = 1
while True:

    sendframe(frame_count)
    print("frame sent")
    sleep(1)
    
    readframe()

    frame_count += 1
    
