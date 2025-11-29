import spidev
import time


class MicLights:
    """Control ReSpeaker 2-Mic APA102 LEDs via SPI."""

    def __init__(self, num_leds=2, bus=0, device=0):
        self.num_leds = num_leds
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 8000000

    def _send_frame(self, data):
        start_frame = [0x00] * 4
        end_frame = [0xFF] * ((self.num_leds + 15) // 16)
        self.spi.xfer2(start_frame + data + end_frame)

    def set_color(self, brightness=0x1F, red=0, green=0, blue=0):
        led_frame = [0xE0 | (brightness & 0x1F), blue & 0xFF, green & 0xFF, red & 0xFF]
        self._send_frame(led_frame * self.num_leds)

    def off(self):
        self.set_color(0, 0, 0, 0)


# --- TEST SEQUENCE ---

if __name__ == "__main__":
    lights = MicLights()

    try:
        print("Red @ 50% brightness")
        lights.set_color(brightness=0x10, red=255, green=0, blue=0)
        time.sleep(2)

        print("Green @ 50% brightness")
        lights.set_color(brightness=0x10, red=0, green=255, blue=0)
        time.sleep(2)

        print("Blue @ 50% brightness")
        lights.set_color(brightness=0x10, red=0, green=0, blue=255)
        time.sleep(2)

        print("Amber (255,100,0) @ 50% brightness")
        lights.set_color(brightness=0x10, red=255, green=100, blue=0)
        time.sleep(2)

        print("Amber (255,165,0) @ full brightness")
        lights.set_color(brightness=0x1F, red=255, green=165, blue=0)
        time.sleep(2)

        print("Amber (255,100,0) @ full brightness")
        lights.set_color(brightness=0x1F, red=255, green=100, blue=0)
        time.sleep(2)

        print("Off")
        lights.off()

    except KeyboardInterrupt:
        lights.off()
