#!/usr/bin/env python3

from random import randint

def build_frame(percentage=0):

    # steadily increase percentage to simulate changing values
    
    # create frame buffer
    frame = bytearray(33)

    frame[0] = 42  # version number
    frame[1] = 84  # PROM
    frame[2] = 1   # status

    ap = percentage * 15.2
    MAP = int((ap+1.5) * 18.6)
    print(ap)
    frame[3] = min(MAP, 255)  # mass air pressure
    
    wt = percentage * 247
    CTS = int((wt+40)/1.125)
    frame[4] = CTS  # coolant temperature

    at = (1 - percentage) * 90
    IAT = int((at+40)/1.125)
    frame[5] = IAT

    volts12 = percentage * 15.7
    frame[6] = int(volts12*16.24) # system voltage
    volts5 = percentage * 4.98
    frame[7] = int(volts5 * 51.2) # sensor voltage

    # max "rpm" is 8000
    rpm = percentage * 8000 if percentage > 0 else 100
    
    # convert to milliseconds between spark plug firing
    gap = int(20000000/rpm)

    # break 16-bit value into two bytes
    lowerG = gap & 0xFF
    upperG = (gap >> 8) & 0xFF
    frame[8] = lowerG
    frame[9] = upperG
    # print("gap: {} upper: 0x{:02X} lower: 0x{:02X}".format(gap, upperG, lowerG))

    tp = percentage * 2.55
    frame[12] = int(tp)

    sa = percentage * 50
    frame[13] = int(sa)



    return frame

class ECUSim():

    def __init__(self):
        raise NotImplemented("need to define uart interface")

    def send(self, frame):

        # signal the start of the frame
        self.uart.write(b'\x00')

        # send each byte of the frame
        for b in frame:

            # if the value is 255, send twice to avoid confusion with endframe marker
            if b == 255:
                self.uart.write(b'\xFF')
            
            # send frame value
            self.uart.write(bytes([b]))
        
        # signal the end of the frame
        self.uart.write(b'\xFF')

    def receive(self):
        raise NotImplemented("abstract base class")

class PycomSim(ECUSim):

    def __init__(self):
        from machine import UART, ADC
        self.uart = UART(1, baudrate=62500)

class UnixSim(ECUSim):

    def __init__(self):
        import serial
        self.uart = serial.Serial('/dev/ttys006')


import sys
from time import sleep

if __name__ == "__main__":

    ecuSim = None

    if sys.platform == 'WiPy':
        ecuSim = PycomSim()
    elif sys.platform in ['darwin', 'raspberrypi']:
        ecuSim = UnixSim()
    else:
        raise NotImplemented("unsupported architecture")

    print("sending frame...", end='')
    count = 50
    while True:

        iters = randint(1, 20)

        for i in range(1, iters):
            frame = build_frame(count/100)
            ecuSim.send(frame)
            print(".", end='')
            sleep(1)

        nval = randint(-10, 10)

        count = (count + nval) % 100
        sleep(1)


# connect TX -> RX to verify sending
# def readframe():
#     while uart.any():
#         raw = uart.read(1)
#         print("{}".format(raw))


# manually send frames
# sendframe(10)
# sendframe(20)


# continually send frame. use frame count to increase values
# frame_count = 1
# while True:

#     sendframe(frame_count)
#     print("frame sent")
#     sleep(1)
    
#     readframe()

#     frame_count += 1
    
