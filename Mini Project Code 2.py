# Mini Project Pi Pico 2 Version 2.1

import board
import digitalio
import adafruit_matrixkeypad
import time
import lcd
import i2c_pcf8574_interface
import busio
import pwmio
from adafruit_motor import servo

i2c = busio.I2C(scl=board.GP1, sda=board.GP0)
address = 0x3F
i2c = i2c_pcf8574_interface.I2CPCF8574Interface(i2c, address)
display = lcd.LCD(i2c, num_rows=2, num_cols=16)
display.set_backlight(True)
display.set_display_enabled(True)

# Define the keypad matrix and corresponding keys
keys = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

# Define the GPIO pins connected to the keypad rows and columns
rows = [digitalio.DigitalInOut(pin) for pin in (board.GP15, board.GP14, board.GP13, board.GP12)]
cols = [digitalio.DigitalInOut(pin) for pin in (board.GP11, board.GP10, board.GP9, board.GP8)]

# Initialize the matrix keypad object
keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)

# Servo Motor
pwm = pwmio.PWMOut(board.GP2, duty_cycle=2 ** 15, frequency=50)
my_servo = servo.Servo(pwm, min_pulse=500, max_pulse=2500)

# Initialize variables
entered_password = ""
set_password_mode = False

display.clear()
display.set_cursor_pos(0, 0)
display.print("To set Password")
display.set_cursor_pos(1, 0)
display.print("Press A")
time.sleep(2)

# Initialize servo position flag
servo_position = 0

while True:
    # Get the key pressed on the keypad
    key = keypad.pressed_keys

    # If a key is pressed, handle it
    if key:
        # Get the first key pressed (ignore multiple keys)
        pressed_key = key[0]
        time.sleep(0.5)

        # Handle the pressed key
        if pressed_key == '#':
            if set_password_mode:
                if len(entered_password) > 0:
                    password = entered_password
                    display.clear()
                    display.set_cursor_pos(0, 0)
                    display.print("Password set")
                    display.set_cursor_pos(1, 0)
                    display.print("{}".format(password))
                    set_password_mode = False
                    time.sleep(2)
                    display.clear()
                else:
                    display.clear()
                    display.set_cursor_pos(0, 0)
                    display.print("Invalid password")
                    display.set_cursor_pos(1, 0)
                    display.print("Enter password")
            else:
                # Check if the entered password is correct
                
                if entered_password == password:
                    print("Password accepted.")
                    display.clear()
                    display.set_cursor_pos(0, 0)
                    display.print("Opening...")
                    time.sleep(2)

                    # Control the servo based on the pressed key
                
                    for angle in range(0, 90, 20):  
                        my_servo.angle = angle
                    
                    time.sleep(10)
                    
                    for angle in range(90, 0, -20):  
                        my_servo.angle = angle
                    
                    display.clear()
                    display.set_cursor_pos(0, 0)
                    display.print("Locking...")
                    time.sleep(20)
                    
                    display.clear()
                    display.set_cursor_pos(0, 0)
                    display.print("Door locked")
                    time.sleep(2)
                    
                    display.clear()
                    display.set_cursor_pos(0, 0)
                    display.print("Enter Password")
                    time.sleep(2)
                    
                else:
                    print("Incorrect password.")
                    display.clear()
                    display.set_cursor_pos(0, 0)
                    display.print("Incorrect password")
                entered_password = ""  # Reset entered password
        elif pressed_key == 'A':
            if not set_password_mode:
                entered_password = ""
                set_password_mode = True
                display.clear()
                display.set_cursor_pos(0, 0)
                display.print("Set password")
                display.set_cursor_pos(1, 0)
                display.print("Enter new pass")
        else:
            entered_password += pressed_key  # Add the pressed key to entered password
            print("Entered password:", entered_password)
            display.clear()
            display.set_cursor_pos(0, 0)
            display.print("Enter password")
            display.set_cursor_pos(1, 0)
            display.print("{}".format(entered_password))

