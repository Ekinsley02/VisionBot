/*
#include <ArduinoBLE.h>

// Custom UUIDs matching the OpenMV code.
#define SERVICE_UUID        "12345678-1234-5678-1234-56789abcdef0"
#define CHARACTERISTIC_UUID "12345678-1234-5678-1234-56789abcdef1"

void setup() {
  Serial.begin(115200);
  while (!Serial);

  if (!BLE.begin()) {
    Serial.println("❌ Failed to initialize BLE!");
    while (1);
  }

  Serial.println("🔍 Scanning for OpenMV BLE...");
  BLE.scan();  // Start scanning for peripherals.
}

void loop() {
  BLEDevice peripheral = BLE.available();

  if (peripheral) {
    Serial.print("📡 Found device: ");
    Serial.print(peripheral.address());
    Serial.print(" [");
    Serial.print(peripheral.localName());
    Serial.print("], RSSI: ");
    Serial.println(peripheral.rssi());

    if (String(peripheral.localName()) == "OpenMV_BLE") {
      Serial.println("✅ Found OpenMV_BLE! Attempting to connect...");
      BLE.stopScan();

      if (peripheral.connect()) {
        Serial.println("🔗 Connected!");

        if (peripheral.discoverAttributes()) {
          Serial.println("✅ Service discovered!");

          BLECharacteristic binary_characteristic;
          bool characteristicFound = false;
          
          // Iterate through discovered characteristics.
          for (int i = 0; i < peripheral.characteristicCount(); i++) {
            BLECharacteristic tempChar = peripheral.characteristic(i);
            Serial.print("🔍 Found characteristic: ");
            Serial.println(tempChar.uuid());
            
            if (String(tempChar.uuid()) == String(CHARACTERISTIC_UUID)) {
              Serial.println("✅ Found matching characteristic!");
              binary_characteristic = tempChar;
              characteristicFound = true;
              break;
            }
          }

          if (characteristicFound) {
            while (peripheral.connected()) {
              if (binary_characteristic.canRead()) {
                uint8_t value;
                binary_characteristic.readValue(&value, sizeof(value));
                Serial.print("📥 Received: ");
                Serial.println(value ? "🔴 Yellow Detected (1)" : "⚪ No Yellow (0)");
              }
              delay(1000);
            }
          } else {
            Serial.println("❌ ERROR: Could not find the characteristic! Disconnecting...");
          }
          peripheral.disconnect();
          BLE.scan();
        } else {
          Serial.println("❌ Failed to discover attributes. Disconnecting...");
          peripheral.disconnect();
          BLE.scan();
        }
      } else {
        Serial.println("❌ Connection failed, scanning again...");
        BLE.scan();
      }
    }
  }
}
*/
#include <ArduinoBLE.h>

// Match these with your custom 128-bit UUIDs on the OpenMV side.
#define SERVICE_UUID        "12345678-1234-5678-1234-56789abcdef0"
#define CHARACTERISTIC_UUID "12345678-1234-5678-1234-56789abcdef1"

BLECharacteristic binaryCharacteristic;

void setup() {
  Serial.begin(115200);
  while (!Serial);

  if (!BLE.begin()) {
    Serial.println("❌ Failed to initialize BLE!");
    while (1);
  }

  Serial.println("🔍 Scanning for OpenMV_BLE...");
  BLE.scan();  // Start scanning for peripherals.
}

void loop() {
  BLEDevice peripheral = BLE.available();

  // If we see a new peripheral:
  if (peripheral) {
    Serial.print("📡 Found device: ");
    Serial.print(peripheral.address());
    Serial.print(" [");
    Serial.print(peripheral.localName());
    Serial.print("], RSSI: ");
    Serial.println(peripheral.rssi());

    if (peripheral.localName() == "OpenMV_BLE") {
      Serial.println("✅ Found OpenMV_BLE! Attempting to connect...");
      BLE.stopScan();

      if (peripheral.connect()) {
        Serial.println("🔗 Connected!");

        if (peripheral.discoverAttributes()) {
          Serial.println("✅ Service discovered!");

          // Attempt to find the characteristic we're interested in
          binaryCharacteristic = peripheral.characteristic(CHARACTERISTIC_UUID);

          if (binaryCharacteristic) {
            Serial.println("✅ Found matching characteristic!");

            // -- Subscribe to notifications --
            if (binaryCharacteristic.canSubscribe()) {
              if (!binaryCharacteristic.subscribe()) {
                Serial.println("❌ Subscription failed!");
              } else {
                Serial.println("🔔 Subscribed to notifications!");
              }
            } else {
              Serial.println("⚠️ Characteristic does not support subscribe!");
            }

            // Main loop while connected
            while (peripheral.connected()) {
              // If there's a new notification, read it
              if (binaryCharacteristic.valueUpdated()) {
                uint8_t value;
                binaryCharacteristic.readValue(&value, sizeof(value));

                Serial.print("📥 Received: ");
                if (value == 2) {
                  Serial.println("🟢 Keep-Alive (2)");
                } else if (value == 1) {
                  Serial.println("🔴 Yellow Detected (1)");
                } else {
                  Serial.println("⚪ No Yellow (0)");
                }
              }
              delay(100);
            }

            Serial.println("❌ Disconnected!");
            peripheral.disconnect();
            BLE.scan();
          } else {
            Serial.println("❌ ERROR: Could not find the characteristic!");
            peripheral.disconnect();
            BLE.scan();
          }
        } else {
          Serial.println("❌ Failed to discover attributes. Disconnecting...");
          peripheral.disconnect();
          BLE.scan();
        }
      } else {
        Serial.println("❌ Connection failed, scanning again...");
        BLE.scan();
      }
    }
  }
}

