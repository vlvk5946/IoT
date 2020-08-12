import RPi.GPIO as GPIO
from time import sleep
import spidev

LED_1 = 4
LED_2 = 5
LED_3 = 14
LED_4 = 15
LED = [LED_1, LED_2, LED_3, LED_4]

spi = spidev.SpiDev()
CDS_CHANNEL = 0


def initMcp3208():
    spi.open(0, 0)  # open(bus,device), device 0 - CE0(GPIO8), device 1 - CE1(GPIO7)
    spi.max_speed_hz = 1000000  # set 1MHz
    spi.mode = 3  # set 0b110


def buildReadCommand(channel):
    '''
    # Return python list of 3 bytes
    #   Build a python list using [1, 2, 3]
    #   First byte is the start bit
    #   Second byte contains single ended along with channel #
    #   3rd byte is 0
    '''

    startBit = 0x04
    singleEnded = 0x08

    configBit = [startBit | ((singleEnded | (channel & 0x07)) >> 2), (channel & 0x07) << 6, 0x00]

    return configBit


def processAdcValue(result):
    '''Take in result as array of three bytes.
       Return the two lowest bits of the 2nd byte and
       all of the third byte'''
    byte2 = (result[1] & 0x0F)
    return (byte2 << 8) | result[2]


def analogRead(channel):
    if (channel > 7) or (channel < 0):
        return -1

    r = spi.xfer2(buildReadCommand(channel))
    adc_out = processAdcValue(r)
    return adc_out


def controlMcp3208(channel):
    analogVal = analogRead(channel)
    return analogVal


def readSensor(channel):
    return controlMcp3208(channel)


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup([LED_1, LED_2, LED_3, LED_4], GPIO.OUT, initial=False)
    initMcp3208()
    print("Setup pin as outputs")

    try:
        while True:
            readVal = readSensor(CDS_CHANNEL)

            voltage = readVal * 4.096 / 4096
            print("CDS Val=%d\tVoltage=%f" % (readVal, voltage))
            if readVal > 3000:
                GPIO.output([LED_1, LED_2, LED_3, LED_4], GPIO.LOW)
            elif readVal > 2500:
                GPIO.output([LED_2, LED_3, LED_4], GPIO.LOW)
                GPIO.output(LED_1, GPIO.HIGH)
            elif readVal > 1500:
                GPIO.output([LED_3, LED_4], GPIO.LOW)
                GPIO.output([LED_1, LED_2], GPIO.HIGH)
            elif readVal > 500:
                GPIO.output([LED_4], GPIO.LOW)
                GPIO.output([LED_1, LED_2, LED_3], GPIO.HIGH)
            else:
                GPIO.output([LED_1, LED_2, LED_3, LED_4], GPIO.HIGH)

            sleep(2)
    except KeyboardInterrupt:
        GPIO.cleanup()
        spi.close()


if __name__ == '__main__':
    main()
