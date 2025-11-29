#  Required python imports
import spidev
import time
import threading

# Required local imports
from utils.logging import logger


class MicLights:
    """Control ReSpeaker 2-Mic APA102 LEDs via SPI."""

    def __init__(self, num_leds: int = 3, bus: int = 0, device: int = 0) -> None:
        """
        Initialize SPI for LED control.
        Args:
            num_leds (int): Number of LEDs (default: 2 for ReSpeaker 2-Mic).
            bus (int): SPI bus (default: 0).
            device (int): SPI device (default: 0).
        """
        self.num_leds = num_leds
        self.spi = spidev.SpiDev()
        self._available = False
        self._pulsing = False
        self._pulse_thread = None
        try:
            self.spi.open(bus, device)
            self.spi.max_speed_hz = 8000000
            self._available = True
        except Exception as e:
            logger.error(f"Failed to initialize mic lights SPI: {e}")

    def _send_frame(self, led_data: list[int]) -> None:
        """Internal method to send SPI data with start/end frames."""
        if not self._available:
            return
        try:
            start_frame = [0x00] * 4
            end_frame = [0xFF] * ((self.num_leds + 15) // 16)
            self.spi.xfer(start_frame + led_data + end_frame)
        except Exception as e:
            logger.error(f"Error controlling mic lights: {e}")

    def set_color(
        self, brightness: int = 0x1F, red: int = 0, green: int = 0, blue: int = 0
    ) -> None:
        """
        Set all LEDs to the same RGB color.
        Args:
            brightness (int): 0x00 (min) to 0x1F (max).
            red (int): 0-255.
            green (int): 0-255.
            blue (int): 0-255.
        """
        if not self._available:
            return
        led_frame = [
            0xE0 | (brightness & 0x1F),  # Brightness + header
            blue & 0xFF,  # Blue
            green & 0xFF,  # Green
            red & 0xFF,  # Red
        ]
        self._send_frame(led_frame * self.num_leds)

    # Functions to control the mic lights scheme
    def lights_idle(self, brightness: int = 0x08) -> None:
        """Dim blue when idle."""
        if not self._available:
            return
        self.set_color(brightness=brightness, red=0, green=0, blue=255)

    def lights_wake_word(self) -> None:
        """Set LEDs to cyan while listening."""
        if not self._available:
            return
        self.set_color(brightness=0x1F, red=0, green=255, blue=255)

    def lights_listening(self) -> None:
        """Set LEDs to amber/orange while processing."""
        if not self._available:
            return
        self.set_color(brightness=0x10, red=255, green=100, blue=0)

    def lights_pulsing_processing(self, duration=5) -> None:
        if not self._available:
            return

        def pulse():
            end_time = time.time() + duration
            while time.time() < end_time and self._pulsing:
                for b in range(5, 32, 2):
                    if not self._pulsing:
                        break
                    self.set_color(brightness=b, red=0, green=255, blue=255)
                    time.sleep(0.03)
                for b in range(31, 4, -2):
                    if not self._pulsing:
                        break
                    self.set_color(brightness=b, red=0, green=255, blue=255)
                    time.sleep(0.03)
            # When stopped, don't clear LEDs here

        self._pulsing = True
        self._pulse_thread = threading.Thread(target=pulse, daemon=True)
        self._pulse_thread.start()

    def stop_pulsing(self) -> None:
        self._pulsing = False
        # Wait for thread to finish cleanup
        if self._pulse_thread:
            self._pulse_thread.join()

    # Not used yet, but keeping to use later
    def lights_error(self, flashes=3, interval=0.3) -> None:
        """Flash red to indicate an error."""
        if not self._available:
            return
        for _ in range(flashes):
            self.set_color(brightness=0x1F, red=255, green=0, blue=0)
            time.sleep(interval)
            self.off()
            time.sleep(interval / 2)

    def off(self) -> None:
        """Turn off all LEDs."""
        self.set_color(brightness=0x00, red=0, green=0, blue=0)

    def __del__(self) -> None:
        """Cleanup SPI on object destruction."""
        try:
            self.spi.close()
        except Exception:
            pass
