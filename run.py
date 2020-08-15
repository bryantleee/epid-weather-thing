from update_epd import update_epd
import time

while True:
    update_epd()
    time.sleep(900 - time.time() % 900)