import ctypes
import os

def get_current_wallpaper():
    SPI_GETDESKWALLPAPER = 0x0073
    buffer = ctypes.create_unicode_buffer(260)
    ctypes.windll.user32.SystemParametersInfoW(SPI_GETDESKWALLPAPER, 260, buffer, 0)
    return buffer.value

if __name__ == "__main__":
    current_wallpaper = get_current_wallpaper()
    print(f"Current Wallpaper Path: {current_wallpaper}")
    print(f"Does it exist? {os.path.exists(current_wallpaper)}")
