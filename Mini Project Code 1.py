# Mini Project Pi Pico 1 Version 4.0

import asyncio
import board
import digitalio
import time
import adafruit_dht
import lcd
import i2c_pcf8574_interface
import busio
import os
import pwmio
import ipaddress
import wifi
import socketpool
import ssl
import adafruit_requests
import microcontroller
from adafruit_motor import stepper
from adafruit_motor import servo
import adafruit_hcsr04

# Get wifi and blynk token details from a settings.toml file
print(os.getenv("test_env_file"))
ssid = os.getenv("WIFI_SSID")
password = os.getenv("WIFI_PASSWORD")
blynkToken = os.getenv("blynk_auth_token")

# Write API
def write(token,pin,value):
        api_url = "https://blynk.cloud/external/api/update?token="+token+"&"+pin+"="+value
        response = requests.get(api_url)
        if "200" in str(response):
                print("Value successfully updated")
        else:
                print("Could not find the device token or wrong pin format")
# Read API
def read(token,pin):
        api_url = "https://blynk.cloud/external/api/get?token="+token+"&"+pin
        response = requests.get(api_url)
        return response.content.decode()
    
# Connect to Wi-Fi AP
print(f"Initializing...")
wifi.radio.connect(ssid,password)
print("connected!\n")
pool = socketpool.SocketPool(wifi.radio)
print("IP Address: {}".format(wifi.radio.ipv4_address))
print("Connecting to WiFi '{}' ...\n".format(ssid), end="")
requests = adafruit_requests.Session(pool, ssl.create_default_context())
    
    
#initialize button
button = [0,0]
Button = (board.GP0,board.GP1)

for i in range(2):
    button[i] = digitalio.DigitalInOut(Button[i])
    button[i].direction = digitalio.Direction.INPUT

# initilize led
led = digitalio.DigitalInOut(board.GP2)
led.direction = digitalio.Direction.OUTPUT

# initilize servo
pwm = pwmio.PWMOut(board.GP3, duty_cycle=2 ** 15, frequency=50)
my_servo = servo.Servo(pwm, min_pulse = 500, max_pulse = 2500)

#initilize LCD Display
i2c = busio.I2C(scl=board.GP5, sda=board.GP4)
address = 0x27 #0x3F
i2c = i2c_pcf8574_interface.I2CPCF8574Interface(i2c, address)
display = lcd.LCD(i2c, num_rows=2, num_cols=16)
display.set_backlight(True)
display.set_display_enabled(True)

#initialize IR sensor
ir = [0,0,0]
IR = (board.GP6,board.GP7,board.GP8)

for i in range(3):
    ir[i] = digitalio.DigitalInOut(IR[i])
    ir[i].direction = digitalio.Direction.INPUT

#initialize vibration sensor
vibration = digitalio.DigitalInOut(board.GP9)
vibration.direction = digitalio.Direction.INPUT

#initialize buzzer
buzzer = digitalio.DigitalInOut(board.GP10)
buzzer.direction = digitalio.Direction.OUTPUT

#initialize ultrasonic
sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.GP13, echo_pin=board.GP12)

def Read_Ultrasonic():
    time.sleep(0.1)
    return sonar.distance

# intilize stepper motor 1
coils1 = (
    digitalio.DigitalInOut(board.GP14),  # A1
    digitalio.DigitalInOut(board.GP15),  # A2
    digitalio.DigitalInOut(board.GP16),  # B1
    digitalio.DigitalInOut(board.GP17),  # B2
)

for coil in coils1:
    coil.direction = digitalio.Direction.OUTPUT

motor1 = stepper.StepperMotor(coils1[0], coils1[1], coils1[2], coils1[3], microsteps=None)

# intilize stepper motor 2
coils2 = (
    digitalio.DigitalInOut(board.GP18),  # A1
    digitalio.DigitalInOut(board.GP19),  # A2
    digitalio.DigitalInOut(board.GP20),  # B1
    digitalio.DigitalInOut(board.GP21),  # B2
)

for coil in coils2:
    coil.direction = digitalio.Direction.OUTPUT

motor2 = stepper.StepperMotor(coils2[0], coils2[1], coils2[2], coils2[3], microsteps=None)

item_choose = 0
DELAY = 0.002
STEPS = 100000
noone = 1
revenue = 0.00
stock1 = 0
stock2 = 0
balance10 = 0
balance50 = 0
previousbuy = ""
start_time = time.monotonic()
display_interval = 2.0
display_state = False
func_V1 = 0
func_V2 = 0

def insufficient():
    display.clear()
    display.set_cursor_pos(0, 0)
    display.print("Insufficient")
    display.set_cursor_pos(1, 0)
    display.print("Fund")
    time.sleep(0.2)
    
def alarm():
    write(blynkToken,"V0","1")
    write(blynkToken,"V1","Violation Detected")
    
    while True:
        buzzer.value = True
        display.clear()
        display.set_cursor_pos(0, 0)
        display.print("Alert")
        display.set_cursor_pos(1, 0)
        display.print("Vandalism")
        buzzer.value = False
        status = read(blynkToken,"V0")
        if status == "0":
            write(blynkToken,"V1","No Disturbance")
            display.clear()
            buzzer.value = False
            func_V1 = 0
            break
        time.sleep(0.02)

def theif():
    write(blynkToken,"V0","1")
    write(blynkToken,"V1","Theif Detected")
    
    while True:
        buzzer.value = True
        display.clear()
        display.set_cursor_pos(0, 0)
        display.print("Kyyaaaaaa")
        display.set_cursor_pos(1, 0)
        display.print("Theifff!!")
        
        status = read(blynkToken,"V0")
        if status == "0":
            write(blynkToken,"V1","No Disturbance")
            display.clear()
            buzzer.value = False
            func_V1 = 0
            break
        time.sleep(0.02)

while True:
    coin10 = 0
    coin50 = 0
    balance = 0.00
    led.value = False
    display.clear()
    Distance = Read_Ultrasonic()
    noone = 1
    
    revenue = round(revenue, 2)
    
    if func_V1 == 0 or func_V2 == 0:
        write(blynkToken,"V0","0")
        write(blynkToken,"V1","No Disturbance")
        write(blynkToken,"V2",str(revenue))
        func_V1 = 1
        func_V2 = 1
        
    stock1 = int(read(blynkToken,"V3"))
    stock2 = int(read(blynkToken,"V4"))
    balance10 = int(read(blynkToken,"V5"))
    balance50 = int(read(blynkToken,"V6"))
    dispose = int(read(blynkToken,"V8"))
    restock = int(read(blynkToken,"V9"))
    print(Distance)
    
    if ir[2].value == False:
        theif()
        
    if vibration.value == True:
        alarm()
    
    if restock == 1:
        while True:
            restock = int(read(blynkToken,"V9"))
            if restock == 0:
                break
            
    if Distance < 70 :
        
        led.value = True
        while True:
            
            if dispose == 1:
                while True:
                    display.clear()
                    display.set_cursor_pos(0, 0)
                    display.print("DISPOSING")
                    display.set_cursor_pos(1, 0)
                    display.print("COIN")
                    for angle in range(80, 180, 5):  # dispense 50 cent
                        my_servo.angle = angle
                        time.sleep(0.01)
                        
                    for angle in range(110, 0, -5):  # dispense 10 cent
                        my_servo.angle = angle
                        time.sleep(0.01)
                
                    dispose = int(read(blynkToken,"V8"))
                    
                    if dispose == 0:
                        break
            Distance = Read_Ultrasonic()
            current_time = time.monotonic()
            elapsed_time = current_time - start_time
            
            if ir[0].value == False:
                break
            elif ir[1].value == False:
                break
            
            if vibration.value == True:
                alarm()
            if ir[2].value == False:
                theif()
            
            if elapsed_time >= display_interval:
                
                if display_state == False:
                    display.clear()
                    display.set_cursor_pos(0, 0)
                    display.print("WELCOME TO")
                    display.set_cursor_pos(1, 0)
                    display.print("MESIN GEDEGANG")
                    display_state = True
                    start_time = current_time
                    print(elapsed_time)
                else:
                    display.clear()
                    display.set_cursor_pos(0, 0)
                    display.print("INSERT COIN")
                    display.set_cursor_pos(1, 0)
                    display.print("TO PURCHASE")
                    start_time = current_time
                    display_state = False
            
            if Distance > 70:
                noone = 0
                break
            
        if noone == 0:
            continue
        
        previous = 0.00
        while True:
            
            if ir[0].value == False:
                coin10 = 1 + coin10
                balance10 = balance10 + 1
                write(blynkToken,"V5",str(balance10))
                
            elif ir[1].value == False:
                coin50 = 1 + coin50
                balance50 = balance50 + 1
                write(blynkToken,"V6",str(balance50))
                
            balance = (coin10 * 0.10) + (coin50 * 0.50)
            
            if balance > previous:
                display.clear()
                display.set_cursor_pos(0, 0)
                display.print("Balance:")
                display.set_cursor_pos(1, 0)
                display.print("RM{:5.2f}".format(balance))
                previous = balance
            
            
            if button[0].value == True:
                
                if balance >= 1.00:
                    item_choose = 0
                    revenue = revenue + 1.00
                    stock1 = stock1 - 1
                    write(blynkToken,"V3",str(stock1))
                    write(blynkToken,"V7","Stock 1")
                    display.clear()
                    display.set_cursor_pos(0, 0)
                    display.print("Item Selected:")
                    display.set_cursor_pos(1, 0)
                    display.print("Stock 1")
                    break
                else:
                    insufficient()
                    display.set_cursor_pos(0, 0)
                    display.print("Balance:")
                    display.set_cursor_pos(1, 0)
                    display.print("RM{:5.2f}".format(balance))
            if button[1].value == True:
                
                if balance >= 1.50:
                    item_choose = 1
                    revenue = revenue + 1.50
                    stock2 = stock2 - 1
                    write(blynkToken,"V4",str(stock2))
                    write(blynkToken,"V7","Stock 2")
                    display.clear()
                    display.set_cursor_pos(0, 0)
                    display.print("Item Selected:")
                    display.set_cursor_pos(1, 0)
                    display.print("Stock 2")
                    break
                else:
                    insufficient()
                    display.set_cursor_pos(0, 0)
                    display.print("Balance:")
                    display.set_cursor_pos(1, 0)
                    display.print("RM{:5.2f}".format(balance))
        
        if item_choose == 1:
            balance = balance - 1.00
            
            for step in range(STEPS):  
                motor1.onestep(style=stepper.DOUBLE)
                time.sleep(DELAY)
                
                if ir[2].value == False:
                    break
                
        elif item_choose == 0:
            balance = balance - 1.50
            
            for step in range(STEPS):  
                motor2.onestep(style=stepper.DOUBLE)
                time.sleep(DELAY)
                
                if ir[2].value == False:
                    break 
                
        while True:
            
            balance = round(balance, 2)
                
            if balance >= 0.5 :
                balance = balance - 0.5
                balance50 = balance50 - 1
                write(blynkToken,"V6",str(balance50))
                print(balance50)
                print("dispense 50")
                for angle in range(80, 180, 5):  # dispense 50 cent
                    my_servo.angle = angle
                    time.sleep(0.1)
                    
            elif balance == 0.0 :
                my_servo.angle = 90
                break
                    
            elif balance < 0.5 :
                balance = balance - 0.1
                balance10 = balance10 - 1
                print(balance10)
                write(blynkToken,"V5",str(balance10))
                print("dispense 10")
                for angle in range(110, 0, -5):  # dispense 10 cent
                    my_servo.angle = angle
                    time.sleep(0.1)

                        
               
        display.clear()
        display.set_cursor_pos(0, 0)
        display.print("THANK YOU")
        display.set_cursor_pos(1, 0)
        display.print("AND ENJOY")
        func_V2 = 0
        time.sleep(2)
        
        
    
                
                    
                



