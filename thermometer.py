import board
import busio as io
import time
import board
import adafruit_dht
from digitalio import DigitalInOut
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
from gpiozero import LED,Button
from signal import pause
import RPi.GPIO as GPIO
count = 0
back = 0

dutyCycle = 0

GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.OUT)

LEDS= GPIO.PWM(16, 100)
LEDS.start(dutyCycle)
blue = LED(6)
yellow = LED(21)
LEDR = 16
button = Button(26)
buttond = Button(13)
buttonsmart = Button(18)
i2c = io.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)


reset_pin = DigitalInOut(board.D5) # any pin!
font = ImageFont.load_default()


dhtDevice = adafruit_dht.DHT22(board.D20, use_pulseio=False)
def counts():
    global count
    count = count + 1
    print(count)

    if count > 0:
        yellow.on()
        blue.off()
    if count == 0:
        yellow.off()
        blue.off()
    if count < 0:
        blue.on()
        yellow.off()
  
def countsd():
    global count
    count = count - 1
    print(count)

    if count > 0:
        yellow.on()
        blue.off()
    if count == 0:
        yellow.off()
        blue.off()
    if count < 0:
        blue.on()
        yellow.off()
def smartcount():
    global count
    global temperature_c
    global back
    back = back +1
    print(back)
    if back % 2 == 0:
        count = 0
        
        print(count)
    else:
        count = round(18-temperature_c,1)
        print(temperature_c)
    if count > 0:
        yellow.on()
        blue.off()
    if count == 0:
        yellow.off()
        blue.off()
    if count < 0:
        blue.on()
        yellow.off()
def temp_fire():
    global temperature_c
    global dutyCycle
    global LEDS
    for dutyCycle in range(301): 
        
        LEDS.ChangeDutyCycle(abs((dutyCycle % 200)-100))
        time.sleep(0.01)
        

    
while True:
    try:
        
        image = Image.new("1", (oled.width, oled.height))
        draw = ImageDraw.Draw(image)
        # Print the values to the serial port
        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dhtDevice.humidity
        
        req_temp_c = temperature_c + count
        print(req_temp_c)
        req_temp_f = (temperature_c + count) * (9 / 5) + 32
        temps = "Temp: {:.1f} F / {:.1f} C".format(
                temperature_f, temperature_c)
        temphum = "Humidity: {}%".format(humidity)
        tempchange = "Wanted Temp:\n {:.1f} F / {:.1f} C".format(
            req_temp_f, req_temp_c)
        print(
            "Temp: {:.1f} F / {:.1f} C Humidity: {}%".format(
                temperature_f, temperature_c, humidity
            )
        )
        
        textreq = str(tempchange)
        text = str(temps)
        texthum = str(temphum)
        (font_width, font_height) = font.getsize(text)
        
        
        draw.text(
            (oled.width // 2 - font_width // 2, oled.height // 4 - font_height // 1),
            text,
            font=font,
            fill=255,
        )
        draw.text(
            (oled.width // 2 - font_width // 2, oled.height // 4 - font_height // 4),
            texthum,
            font=font,
            fill=255,
        )
        if temperature_c != req_temp_c:
            draw.text(
            (oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 4),
            textreq,
            font=font,
            fill=255,
        )
        oled.image(image)
        oled.show()
        button.when_pressed = counts
        buttond.when_pressed = countsd
        buttonsmart.when_pressed = smartcount
        if humidity >= 60:
            GPIO.output(LEDR, GPIO.HIGH)
        if humidity <60:
            GPIO.output(LEDR, GPIO.LOW)
        if temperature_c > 30:
            temp_fire()
        

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        time.sleep(2)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error

    time.sleep(2)