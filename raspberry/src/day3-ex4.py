import board
import adafruit_dht
import RPi.GPIO as GPIO
from time import sleep

dhtDevice = adafruit_dht.DHT11(board.D17)

ON = 1
OFF = 0

FAN_PIN1 = 18
FAN_PIN2 = 27


def onFan():
    GPIO.output(FAN_PIN1, GPIO.HIGH)
    GPIO.output(FAN_PIN2, GPIO.LOW)


def offFan():
    GPIO.output(FAN_PIN1, GPIO.LOW)
    GPIO.output(FAN_PIN2, GPIO.LOW)


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(FAN_PIN1, GPIO.OUT, initial=False)
    GPIO.setup(FAN_PIN2, GPIO.OUT, initial=False)
    print("Setup FAN pin as outputs")
    print("main() program")

    while True:

        try:
            temperature_c = dhtDevice.temperature
            humidity = dhtDevice.humidity
            print("Temp: {:.1f}C   Humidity: {}%".format(temperature_c, humidity))
            if (temperature_c > 28 or humidity > 50):
                onFan()
            else:
                offFan()

        except RuntimeError as error:
            print(error.args[0])

        sleep(2.0)


if __name__ == '__main__':
    main()
