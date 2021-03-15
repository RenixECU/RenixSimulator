from machine import UART, ADC
from time import sleep

uart = UART(1, baudrate=62500)
adc = ADC()
cts_pin = adc.channel(pin='P15')
volt_pin = adc.channel(pin='P14')
rpm_pin = adc.channel(pin='P13')


def sendframe(frame_count):

    percent = (frame_count % 100) / 100
    
    frame = bytearray(33)
    
    wt = percent * 247
    cts = int((wt+40)/1.125)
    frame[4] = cts

    volts = percent * 255
    frame[6] = int(volts)

    rpm = percent * 8000
    
    gap = int(20000000/rpm)
    lowerG = gap & 0xFF
    upperG = (gap >> 8) & 0xFF

    frame[8] = lowerG
    frame[9] = upperG
    print("gap: {} upper: 0x{:02X} lower: 0x{:02X}".format(gap, upperG, lowerG))


    uart.write(b'\x00')
    for b in frame:
        if b == 255:
            uart.write(b'\xFF')
        uart.write(bytes([b]))
    uart.write(b'\xFF')

    frame_count +=1
    

    # for i in range(0,33):
    #     uart.write(bytearray(frame[i]))

    # uart.write(b'\xFF')

    # uart.write('\x00')
    # for i in range(0,33):
    #     uart.write(b'\x01')
    # uart.write(b'\xFF')

def readframe():
    while uart.any():
        raw = uart.read(1)
        print("{}".format(raw))

frame_count = 1

sendframe(10)
sendframe(20)




# while True:

#     print("start frame")
#     sendframe(frame_count)
#     print("end frame")
#     sleep(1)
#     readframe()

#     frame_count += 1
    
