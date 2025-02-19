# Untitled - By: peppe - Tue Jan 7 2025

'''
import pyb # Import module for board related functions
import sensor # Import the module for sensor related functions
import image # Import module containing machine vision algorithms
import time

redLED = pyb.LED(1) # built-in red LED
blueLED = pyb.LED(3) # built-in blue LED

while(1):
    sensor.reset() # Initialize the camera sensor.
    sensor.set_pixformat(sensor.RGB565) # Sets the sensor to RGB
    sensor.set_framesize(sensor.QVGA) # Sets the resolution to 320x240 px
    sensor.set_vflip(True) # Flips the image vertically
    sensor.set_hmirror(True) # Mirrors the image horizontally

    sensor.skip_frames(time = 3000) # Skip some frames to let the image stabilize

    #sensor.snapshot().save("example.jpg")
'''


# Best camera streaming
'''
import pyb
import sensor
import image
import time

redLED = pyb.LED(1)  # built-in red LED
blueLED = pyb.LED(3) # built-in blue LED

# --- Camera Setup (do this once) ---
sensor.reset()
sensor.set_pixformat(sensor.RGB565)  # Sets the sensor to RGB
sensor.set_framesize(sensor.QVGA)    # Sets resolution to 320x240
sensor.set_vflip(True)               # Flip image vertically
sensor.set_hmirror(True)             # Mirror image horizontally
sensor.skip_frames(time=2000)        # Let the sensor adjust

# --- Main Loop ---
while True:
    img = sensor.snapshot()          # Grab the image
    # You can do further processing here, e.g., find blobs, draw shapes, etc.
    # Example: img.save("example.jpg") if you want to save periodically
'''
'''
import sensor
import image
import time

# Define a color threshold for "yellow."
# You may need to adjust these values based on your environment’s lighting.
# (L Min, L Max, A Min, A Max, B Min, B Max)
# You can use the "Tools > Machine Vision > Threshold Editor" in the OpenMV IDE
# to find good thresholds for your setup.
yellow_threshold = (28, 96, -128, 26, 26, 114)

sensor.reset()                     # Initialize the camera
sensor.set_pixformat(sensor.RGB565)# Use RGB565 for color tracking
sensor.set_framesize(sensor.QVGA)  # Set frame size to 320x240
sensor.skip_frames(time=2000)      # Give the sensor time to adjust
clock = time.clock()               # Create a clock object to track FPS

while True:
    clock.tick()                   # Start measuring frame time
    img = sensor.snapshot()        # Take a picture

    # Find blobs that match the yellow color threshold.
    blobs = img.find_blobs([yellow_threshold],
                           x_stride=2, y_stride=2,         # Speed up the search
                           area_threshold=20, pixels_threshold=20,
                           merge=True)

    # Draw a rectangle around each blob.
    for blob in blobs:
        # Draw a rectangle in green
        img.draw_rectangle(blob.rect(), color=(0,255,0), thickness=2)
        # (Optional) Draw a cross to indicate the center
        img.draw_cross(blob.cx(), blob.cy(), color=(0,255,0))

    # (Optional) Print FPS
    print("FPS:", clock.fps())
'''

'''
import sensor
import image
import time
import pyb  # Import pyb module to control LEDs
import struct
import asyncio
import aioble
import bluetooth
import sensor
import time
from micropython import const

# UUIDs for service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x1815)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A56)

# Advertisement settings
_ADV_APPEARANCE_GENERIC_TAG = const(512)
_ADV_INTERVAL_MS = 250_000

# GATT server setup
binary_service = aioble.Service(_SERVICE_UUID)
binary_characteristic = aioble.Characteristic(binary_service, _CHARACTERISTIC_UUID, read=True, notify=True)
aioble.register_services(binary_service)

# Define a color threshold for "yellow."
# Adjust these values based on your environment’s lighting.
yellow_threshold = (28, 96, -128, 26, 26, 114)

sensor.reset()                     # Initialize the camera
sensor.set_pixformat(sensor.RGB565) # Use RGB565 for color tracking
sensor.set_framesize(sensor.QVGA)   # Set frame size to 320x240
sensor.skip_frames(time=2000)       # Give the sensor time to adjust
clock = time.clock()                # Create a clock object to track FPS

# Initialize LEDs
red_led = pyb.LED(1)   # Red LED
green_led = pyb.LED(2) # Green LED

# Turn on the red LED initially
red_led.on()
green_led.off()

while True:
    clock.tick()                   # Start measuring frame time
    img = sensor.snapshot()        # Take a picture

    # Find blobs that match the yellow color threshold.
    blobs = img.find_blobs([yellow_threshold],
                           x_stride=2, y_stride=2,         # Speed up the search
                           area_threshold=20, pixels_threshold=20,
                           merge=True)

    if blobs:
        # Detected: Turn off red, turn on green
        red_led.off()
        green_led.on()
        binary_characteristic.write(1)
    else:
        # Not detected: Keep red on, turn green off
        red_led.on()
        green_led.off()
        binary_characteristic.write(1)

    # (Optional) Print FPS
    print("FPS:", clock.fps())
'''
'''
import struct
import asyncio
import aioble
import bluetooth
import sensor
import image
import pyb  # Import pyb module to control LEDs
from micropython import const

# UUIDs for BLE service and characteristic
_SERVICE_UUID = bluetooth.UUID("00001815-0000-1000-8000-00805f9b34fb")
_CHARACTERISTIC_UUID = bluetooth.UUID("00002A56-0000-1000-8000-00805f9b34fb")

# BLE Advertisement settings
_ADV_APPEARANCE_GENERIC_TAG = const(512)
_ADV_INTERVAL_MS = 250_000

# Initialize BLE GATT server
binary_service = aioble.Service(_SERVICE_UUID)
binary_characteristic = aioble.Characteristic(binary_service, _CHARACTERISTIC_UUID, read=True, notify=True)
aioble.register_services(binary_service)

# Camera initialization
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)

# Initialize LEDs
red_led = pyb.LED(1)   # Red LED
green_led = pyb.LED(2) # Green LED

async def detect_yellow():
    """ Detects yellow objects and sends data via BLE """
    while True:
        img = sensor.snapshot()
        blobs = img.find_blobs([(28, 96, -128, 26, 26, 114)], merge=True)

        if blobs:
            red_led.off()
            green_led.on()
            binary_characteristic.write(struct.pack("<B", 1))
            print("Yellow Detected: Sent 1")
        else:
            red_led.on()
            green_led.off()
            binary_characteristic.write(struct.pack("<B", 0))
            print("No Yellow: Sent 0")

        await asyncio.sleep(1)

async def peripheral_task():
    """ Advertises BLE connection and waits for a central device to connect """
    while True:
        async with await aioble.advertise(
            _ADV_INTERVAL_MS,
            name="OpenMV_BLE",
            services=[_SERVICE_UUID],  # Ensure service UUID is correctly advertised
            appearance=_ADV_APPEARANCE_GENERIC_TAG,
        ) as connection:
            print("Connection from", connection.device)
            await connection.disconnected()

async def main():
    await asyncio.gather(detect_yellow(), peripheral_task())

asyncio.run(main())
'''
'''
import struct
import asyncio
import aioble
import bluetooth
import sensor
import image
import pyb  # Import pyb module to control LEDs
from micropython import const


# UUIDs for BLE service and characteristic (Must match Arduino)
_SERVICE_UUID = bluetooth.UUID("00001815-0000-1000-8000-00805f9b34fb")
_CHARACTERISTIC_UUID = bluetooth.UUID("00002A56-0000-1000-8000-00805f9b34fb")

# BLE Advertisement settings
_ADV_APPEARANCE_GENERIC_TAG = const(512)
_ADV_INTERVAL_MS = 250_000

# Initialize BLE GATT server
binary_service = aioble.Service(_SERVICE_UUID)
binary_characteristic = aioble.Characteristic(
    binary_service, _CHARACTERISTIC_UUID, read=True, notify=True
)
aioble.register_services(binary_service)  # Ensure service is properly registered

# Camera initialization
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)

# Initialize LEDs
red_led = pyb.LED(1)   # Red LED
green_led = pyb.LED(2) # Green LED

async def detect_yellow():
    """ Detects yellow objects and sends data via BLE """
    while True:
        #img = sensor.snapshot()
        #blobs = img.find_blobs([(28, 96, -128, 26, 26, 114)], merge=True)

        #if blobs:
            #red_led.off()
            #green_led.on()
        #binary_characteristic.write(struct.pack("<B", 1))
            #print("Yellow Detected: Sent 1")
        #else:
            #red_led.on()
            #green_led.off()
            #binary_characteristic.write(struct.pack("<B", 0))
            #print("No Yellow: Sent 0")

        await asyncio.sleep(1)

async def peripheral_task():
    """ Advertises BLE connection and waits for a central device to connect """
    while True:
        print("🔵 Advertising OpenMV BLE...")

        async with await aioble.advertise(
            _ADV_INTERVAL_MS,
            name="OpenMV_BLE",
            services=[_SERVICE_UUID]
        ) as connection:  # ✅ Capture the connection object
            print("🔗 Connected to Central!")
            binary_characteristic.write(struct.pack("<B", 1))
            # ✅ Wait until the central disconnects before restarting advertisement
            await connection.disconnected()
            print("❌ Disconnected! Restarting advertisement...")

async def main():
    await asyncio.gather(peripheral_task())

asyncio.run(main())
'''


#The code under works to use BLE to board with no image detection
'''
import struct
import asyncio
import aioble
import bluetooth
from micropython import const

# Use custom UUIDs so there's no automatic 16-bit compression:
SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
CHAR_UUID    = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef1")

ADV_INTERVAL_MS = const(250_000)

# Create a BLE Service and Characteristic
my_service = aioble.Service(SERVICE_UUID)
my_characteristic = aioble.Characteristic(my_service, CHAR_UUID, read=True, notify=True)
aioble.register_services(my_service)

async def keep_alive_task():
    """Sends a keep-alive notification every 5 seconds."""
    while True:
        # Send an arbitrary value (e.g., 0x02) just to keep the connection alive
        my_characteristic.write(struct.pack("<B", 2))
        print("📤 Sent keep-alive notification.")
        await asyncio.sleep(5)

async def peripheral_task():
    """Advertises, accepts connections, and runs the keep-alive task while connected."""
    while True:
        print("🔵 Advertising OpenMV BLE...")
        # Wait for a central to connect
        async with await aioble.advertise(
            ADV_INTERVAL_MS,
            name="OpenMV_BLE",
            services=[SERVICE_UUID]
        ) as connection:
            print("🔗 Connected to Central!")

            # Start a background task that sends keep-alives
            ka_task = asyncio.create_task(keep_alive_task())

            # Wait until the central disconnects
            await connection.disconnected()
            print("❌ Disconnected! Restarting advertisement...")

            # Cancel the keep-alive task now that we're disconnected
            ka_task.cancel()
            try:
                await ka_task
            except asyncio.CancelledError:
                pass  # Normal when a task is canceled

async def main():
    await peripheral_task()

asyncio.run(main())
'''

import struct
import asyncio
import aioble
import bluetooth
import sensor
import image
import pyb  # For LED control
from micropython import const

# Custom 128-bit UUIDs (match these with your Arduino)
SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
CHAR_UUID    = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef1")

# Lower advertisement interval for quicker discovery (in microseconds)
_ADV_INTERVAL_US = const(40_000)  # ~40ms

# Set up the BLE GATT service and characteristic
my_service = aioble.Service(SERVICE_UUID)
my_characteristic = aioble.Characteristic(my_service, CHAR_UUID, read=True, notify=True)
aioble.register_services(my_service)

# Initialize the camera (if you’re using detection)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)

# Initialize LEDs for visual feedback
red_led = pyb.LED(1)
green_led = pyb.LED(2)

# Yellow detection threshold (adjust as needed)
YELLOW_THRESHOLD = (28, 96, -128, 26, 26, 114)

async def keep_alive_task():
    """Send a keep-alive notification every 1 second."""
    while True:
        my_characteristic.write(struct.pack("<B", 2))  # 2 = keep-alive signal
        print("📤 Sent keep-alive notification.")
        await asyncio.sleep(1)

async def detect_yellow_task():
    """Capture an image, detect yellow, and send the result."""
    while True:
        img = sensor.snapshot()
        await asyncio.sleep_ms(10)  # yield to BLE tasks
        blobs = img.find_blobs([YELLOW_THRESHOLD], merge=True)
        await asyncio.sleep_ms(10)  # yield again
        if blobs:
            red_led.off()
            green_led.on()
            my_characteristic.write(struct.pack("<B", 1))  # 1 = yellow detected
            print("Yellow Detected: Sent 1")
        else:
            red_led.on()
            green_led.off()
            my_characteristic.write(struct.pack("<B", 0))  # 0 = no yellow
            print("No Yellow: Sent 0")
        await asyncio.sleep(2)

async def peripheral_task():
    while True:
        print("🔵 Advertising OpenMV BLE...")
        async with await aioble.advertise(
            _ADV_INTERVAL_US,
            name="OpenMV_BLE",
            services=[SERVICE_UUID]
        ) as connection:
            print("🔗 Connected to Central!")
            # Launch both tasks concurrently
            ka_task = asyncio.create_task(keep_alive_task())
            det_task = asyncio.create_task(detect_yellow_task())
            # Wait until the central disconnects
            await connection.disconnected()
            print("❌ Disconnected! Restarting advertisement...")
            # Cancel background tasks upon disconnect
            ka_task.cancel()
            det_task.cancel()
            try:
                await ka_task
            except asyncio.CancelledError:
                pass
            try:
                await det_task
            except asyncio.CancelledError:
                pass

async def main():
    await peripheral_task()

asyncio.run(main())

