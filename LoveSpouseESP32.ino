#include <NimBLEDevice.h>

// Команды для обработки
#define MAX_COMMAND 14

static uint16_t companyId = 0xFFF0;
#define MANUFACTURER_DATA_PREFIX 0x6D, 0xB6, 0x43, 0xCE, 0x97, 0xFE, 0x42, 0x7C

uint8_t manufacturerDataList[][11] = {
    {MANUFACTURER_DATA_PREFIX, 0xE5, 0x00, 0x00}, // Stop
    {MANUFACTURER_DATA_PREFIX, 0xF4, 0x00, 0x00}, // Low 1
    {MANUFACTURER_DATA_PREFIX, 0xF7, 0x00, 0x00}, // Low 2
    {MANUFACTURER_DATA_PREFIX, 0xF6, 0x00, 0x00}, // Low 3
    {MANUFACTURER_DATA_PREFIX, 0xF1, 0x00, 0x00}, // Low 4
    {MANUFACTURER_DATA_PREFIX, 0xF3, 0x00, 0x00}, // Low 5
    {MANUFACTURER_DATA_PREFIX, 0xE7, 0x00, 0x00}, // Medium
    {MANUFACTURER_DATA_PREFIX, 0xE6, 0x00, 0x00}, // High
    {MANUFACTURER_DATA_PREFIX, 0xE1, 0x00, 0x00}, // Режим 4
    {MANUFACTURER_DATA_PREFIX, 0xD0, 0x00, 0x00}, // Режим 5
    {MANUFACTURER_DATA_PREFIX, 0xD3, 0x00, 0x00}, // Режим 6
    {MANUFACTURER_DATA_PREFIX, 0xE2, 0x00, 0x00}, // Режим 7
    {MANUFACTURER_DATA_PREFIX, 0xED, 0x00, 0x00}, // Режим 8
    {MANUFACTURER_DATA_PREFIX, 0xDC, 0x00, 0x00}, // Режим 9
    {MANUFACTURER_DATA_PREFIX, 0xE9, 0x00, 0x00}  // Режим 10
};

const char *deviceName = "MuSE_Advertiser";

void advertiseManufacturerData(uint8_t index) {
    NimBLEAdvertising *pAdvertising = NimBLEDevice::getAdvertising();
    pAdvertising->stop();
    uint8_t *manufacturerData = manufacturerDataList[index];
    pAdvertising->setManufacturerData(std::string((char *)&companyId, 2) + std::string((char *)manufacturerData, 11));
    pAdvertising->setScanResponse(true);
    pAdvertising->setMinPreferred(0x12);
    pAdvertising->setMaxPreferred(0x02);
    pAdvertising->start();
}

void setup() {
    Serial.begin(115200);
    NimBLEDevice::init(deviceName);
}

void loop() {
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        command.trim();
        int buttonId = command.toInt();

        if (buttonId >= 0 && buttonId <= MAX_COMMAND) {
            advertiseManufacturerData(buttonId);
        }
    }
}
