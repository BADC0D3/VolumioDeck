#!/usr/bin/env python3
from StreamDeck.DeviceManager import DeviceManager

if __name__ == "__main__":
    streamdecks = DeviceManager().enumerate()

    for index, deck in enumerate(streamdecks):
        deck.reset()
        deck.close()
        exit(1)