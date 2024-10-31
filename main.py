#!/usr/bin/env python3
import os
import threading
import traceback
import threading
import signal
from dotenv import load_dotenv
from StreamDeck.DeviceManager import DeviceManager
from volumio import volumio
from mydeckplus import mydeckplus

load_dotenv()  # take environment variables from .env.

URL = os.getenv('VOLUMIO_URL')
VOLUMIO_API = None
MYDECK = None
VOLUME = 20
BRIGHTNESS = 15
FONT_SIZE = 14
AUTOREFRESH = 1

def auto_status():
        tt = threading.Timer(AUTOREFRESH, auto_status)
        tt.start()
        MYDECK.show_status()

def handler(signum, frame):
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        deck.reset()
        deck.close()
        exit(1)
    else:
        pass

def main():
    try:
        MYDECK.stream_deck.set_key_callback(MYDECK.key_change_callback)
        
        if MYDECK.stream_deck.DECK_TYPE == 'Stream Deck +':
            MYDECK.stream_deck.set_dial_callback(MYDECK.dial_change_callback)
            MYDECK.stream_deck.set_brightness(MYDECK.brightness)
        
        MYDECK.show_status()
        MYDECK.load_tiles()
    except Exception as e:
        traceback.print_exc()
        MYDECK.dispose()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    streamdecks = DeviceManager().enumerate()

    for index, deck in enumerate(streamdecks):
        VOLUMIO_API = volumio(URL)
        
        if deck.DECK_TYPE == 'Stream Deck +':
            MYDECK = mydeckplus(deck, VOLUMIO_API, VOLUME, BRIGHTNESS, FONT_SIZE)
        else:
            print(deck.DECK_TYPE)
            print("Sorry, this example only works with the following decks:")
            print("- Stream Deck +")
            continue

        main()
        auto_status()

        for t in threading.enumerate():
            try:
                t.join()
            except RuntimeError:
                pass