#  Required python imports
import spidev
import time
import threading


class MicLights:
    """Control ReSpeaker 2-Mic APA102 LEDs via SPI."""
    
    def __init__(self, num_leds=3, bus=0, device=0):
        """
        Initialize SPI for LED control.
        
        Args:
            num_leds (int): Number of LEDs (default: 2 for ReSpeaker 2-Mic).
            bus (int): SPI bus (default: 0).
            device (int): SPI device (default: 0).
        """
        self.num_leds = num_leds
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 8000000  # APA102 works at 8MHz


    def _send_frame(self, led_data):
        """Internal method to send SPI data with start/end frames."""
        start_frame = [0x00] * 4
        end_frame = [0xFF] * ((self.num_leds + 15) // 16)
        self.spi.xfer(start_frame + led_data + end_frame)


    def set_color(self, brightness=0x1F, red=0, green=0, blue=0):
        """
        Set all LEDs to the same RGB color.
        
        Args:
            brightness (int): 0x00 (min) to 0x1F (max).
            red (int): 0-255.
            green (int): 0-255.
            blue (int): 0-255.
        """
        led_frame = [
            0xE0 | (brightness & 0x1F),  # Brightness + header
            blue & 0xFF,                 # Blue
            green & 0xFF,                # Green
            red & 0xFF                   # Red
        ]
        self._send_frame(led_frame * self.num_leds)


    def set_individual(self, leds):
        """
        Set each LED individually.
        
        Args:
            leds (list of tuples): [(brightness, red, green, blue), ...].
        """
        led_data = []
        for brightness, red, green, blue in leds:
            led_data.extend([
                0xE0 | (brightness & 0x1F),
                blue & 0xFF,
                green & 0xFF,
                red & 0xFF
            ])
        self._send_frame(led_data)


    def lights_wake_word(self, flashes=3, interval=0.2):
        """Flash bright blue when wake word is detected."""
        for _ in range(flashes):
            self.set_color(brightness=0x1F, red=0, green=0, blue=255)
            time.sleep(interval)
            self.off()
            time.sleep(interval / 2)


    def lights_listening(self):
        """Set LEDs to cyan while listening."""
        self.set_color(brightness=0x1F, red=0, green=255, blue=255)


    def lights_processing(self):
        """Set LEDs to amber/orange while processing."""
        self.set_color(brightness=0x10, red=255, green=100, blue=0)


    def lights_speaking(self):
        """Set LEDs to green while speaking."""
        self.set_color(brightness=0x1F, red=0, green=255, blue=0)


    def lights_error(self, flashes=3, interval=0.3):
        """Flash red to indicate an error."""
        for _ in range(flashes):
            self.red()
            time.sleep(interval)
            self.off()
            time.sleep(interval / 2)


    def lights_idle(self, brightness=0x08):
        """Dim blue when idle."""
        self.set_color(brightness=brightness, red=0, green=0, blue=255)


    def lights_pulse_listening(self, duration=5):
        """Optional: Pulse LEDs gently while listening."""
        def pulse():
            end_time = time.time() + duration
            while time.time() < end_time:
                for b in range(5, 32, 2):
                    self.set_color(brightness=b, red=0, green=255, blue=255)
                    time.sleep(0.03)
                for b in range(31, 4, -2):
                    self.set_color(brightness=b, red=0, green=255, blue=255)
                    time.sleep(0.03)
            self.off()
        
        threading.Thread(target=pulse, daemon=True).start()

    def off(self):
        """Turn off all LEDs."""
        self.set_color(brightness=0x00, red=0, green=0, blue=0)

    def __del__(self):
        """Cleanup SPI on object destruction."""
        self.spi.close()