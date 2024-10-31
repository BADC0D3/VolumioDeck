import os
import json
import requests
import math
import datetime
import io

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.ImageHelpers import PILHelper
from StreamDeck.Devices.StreamDeck import DialEventType

class mydeckplus:
    volumio_api = None
    stream_deck = None
    volume      = 20
    brightness  = 15
    font_size   = 14
    
    FONT        = "fonts/RobotoMono-VariableFont_wght.ttf"
    ASSETS_PATH = os.path.join(os.path.dirname(__file__), "icons")
    AUTOREFRESH = 1
    STATUS      = "stopped"
    DISPLAY     = 1
    SOUND       = 1
    UNMUTE      = volume
    PAGING      = 0
    MAX_TILES   = 8
    MAX_PAGES   = 0
    OFFSET      = -1
    TILES       = []

    def __init__(self, deck, volumio, volume, brightness, fontSize):
        self.stream_deck = deck
        self.volumio_api= volumio
        self.volume = volume
        self.brightness = brightness
        self.font_size = fontSize
        
        self.stream_deck.open()
        self.stream_deck.reset()

    def dispose(self):
        self.stream_deck.open()
        self.stream_deck.reset()

    def render_key_img(self, icon_filename, label_text, key):
        icon = Image.open(os.path.join(self.ASSETS_PATH, icon_filename))
        self.render_key_icon(icon, label_text, key)

    def render_key_icon(self, icon, label_text, key):
        image = PILHelper.create_scaled_key_image(self.stream_deck, icon, margins=[0, 0, 20, 0])
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(self.FONT, self.font_size)
        draw.text((image.width / 2, image.height - 15), text=label_text, font=font, anchor="ms", fill="white")
        self.stream_deck.set_key_image(key, PILHelper.to_native_key_format(self.stream_deck, image))

    def show_status(self):
        json_data = self.volumio_api.status()
        self.STATUS = self.get_json_prop(json_data,'status')
        self.volume = self.get_json_prop(json_data,'volume')
        
        font = ImageFont.truetype(self.FONT, self.font_size)
        font2 = ImageFont.truetype(self.FONT, self.font_size * 2)
        img = Image.new('RGB', (800, 100), (0, 0, 0))
        
        try:
            albumart = self.get_json_prop(json_data, 'albumart')
            if albumart.startswith("http"):
                my_res = requests.get(albumart)
                my_img = Image.open(io.BytesIO(my_res.content)).convert("RGBA").resize((100, 100))
            elif albumart.startswith("/albumart?"):
                albumart = "{}{}".format(self.volumio_api.volumio_url, albumart)
                my_res = requests.get(albumart)
                my_img = Image.open(io.BytesIO(my_res.content)).convert("RGBA").resize((100, 100))
            else:
                my_img = Image.open(os.path.join(self.ASSETS_PATH, albumart)).convert("RGBA").resize((100, 100))

            img.paste(my_img, (700, 0), my_img)
        except:
            pass
        
        d = ImageDraw.Draw(img)

        if self.STATUS == "pause":
            status = 'Paused'
            
            height = (80-(self.font_size * 2))/2
            width = (800 - (len(status) * self.font_size * 2))/2
            d.text((width + 30, height),  status,  fill="white", font=font2)
        else:
            d.text((10,  0), "Song Name: {}".format(self.format_text(self.get_json_prop(json_data,'title'))),  fill="white", font=font)
            d.text((10, 18), "   Artist: {}".format(self.format_text(self.get_json_prop(json_data,'artist'))), fill="white", font=font)
            d.text((10, 36), "    Album: {}".format(self.format_text(self.get_json_prop(json_data,'album'))),  fill="white", font=font)
            d.text((10, 54), "     Time: {}".format(self.format_time(self.get_json_prop(json_data,'seek'),self.get_json_prop(json_data,'duration'))), fill="white", font=font)
            d.text((10, 72), "   Volume: {}".format(self.get_json_prop(json_data,'volume')), fill="white", font=font)

            music_info1 = ""
            music_info2 = ""
            
            samplerate  = self.get_json_prop(json_data,'samplerate')
            bitdepth    = self.get_json_prop(json_data,'bitdepth')
            bitrate	    = self.get_json_prop(json_data,'bitrate')
            trackType   = self.get_json_prop(json_data,'trackType')
            channels    = self.get_json_prop(json_data,'channels')
            
            if bitrate:
                music_info1 = bitrate
            elif samplerate:
                music_info1 = samplerate.replace("VBR ", "")
            
            if trackType == "webradio":
                music_info2 = "Web Radio"
            elif bitdepth:
                music_info2 = bitdepth
            else:
                music_info2 = trackType
            
            d.text((600, 0),  self.format_text_right(music_info1,10), fill="white", font=font)
            d.text((600, 18), self.format_text_right(music_info2,10), fill="white", font=font)
            d.text((600, 36), "{} Channels".format(channels),  fill="white", font=font)

        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        self.stream_deck.set_touchscreen_image(img_byte_arr, 0, 0, 800, 100)

    def key_change_callback(self, deck, key, key_state):
        self.stream_deck = deck
        
        if key_state:
            if key > self.OFFSET and key < self.OFFSET + self.MAX_TILES + 1:
                p = self.PAGING if self.PAGING < self.MAX_PAGES else self.MAX_PAGES
                ps = p*self.MAX_TILES
                index = ps + key - self.OFFSET - 1
                self.volumio_api.playback(self.TILES[index]['data'])

            self.show_status()

    def dial_change_callback(self, deck, dial, event, value):
        self.stream_deck = deck
        
        if event == DialEventType.PUSH:
            # Dial 1
            if dial == 0 and value:
                if self.DISPLAY == 1:
                    self.DISPLAY = 0
                    self.stream_deck.set_brightness(0)
                else:
                    self.DISPLAY = 1
                    self.stream_deck.set_brightness(self.brightness)
            # Dial 2
            if dial == 1 and value:
                self.PAGING = 0
                self.load_tiles()

            # Dial 3
            if dial == 2 and value:
                if self.STATUS == 'play':
                    self.volumio_api.command('pause', self.show_status)
                else:
                    self.volumio_api.command('play', self.show_status)

            # Dial 4
            if dial == 3 and value:
                if self.SOUND == 1:
                    self.SOUND = 0
                    self.UNMUTE = self.volume
                    self.volumio_api.volume(0)
                else:
                    self.SOUND = 1
                    self.volumio_api.volume(self.UNMUTE)
        elif event == DialEventType.TURN:
            # Dial 1
            if dial == 0 and value < 0:
                if (self.brightness > 0):
                    self.brightness = self.brightness -5
                else:
                    self.brightness = 0
                self.stream_deck.set_brightness(self.brightness)
            elif dial == 0 and value > 0:
                if (self.brightness < 100):
                    self.brightness = self.brightness +5
                else:
                    self.brightness = 100
                self.stream_deck.set_brightness(self.brightness)

            # Dial 2
            if dial == 1 and value < 0:
                if (self.PAGING > 0):
                    self.PAGING -=1
                else:
                    self.PAGING = 0
                self.map_keys()
            elif dial == 1 and value > 0:
                if (self.PAGING < self.MAX_PAGES):
                    self.PAGING +=1
                else:
                    self.PAGING = self.MAX_PAGES
                self.map_keys()

            # Dial 3
            if dial == 2 and value < 0:
                self.volumio_api.command('prev', self.show_status)
            elif dial == 2 and value > 0:
                self.volumio_api.command('next', self.show_status)

            # Dial 4
            elif dial == 3 and value < 0:
                self.volumio_api.volume_minus()
            elif dial == 3 and value > 0:
                self.volumio_api.volume_increase()

        self.show_status()

    def get_json_prop(self, json_data, prop):
        data = ""
        try:
            data = json_data[prop]
        except:
            pass
        return data

    def format_text(self, text):
        max_char = 50
        if text and len(text) > max_char:
            text = text.split('(')[0]
            if text and len(text) > max_char:
                text = text.split(',')[0]
                if text and len(text) > max_char:
                    text = text.split('&')[0]
                    if text and len(text) > max_char:
                        text = "{}...".format(text[:max_char])
        if text == None:
            text = ""
        
        return text

    def format_text_right(self, text, length):
        if len(text) < length:
            text = "{}{}".format(" " * (length-len(text)), text)
        elif len(text) > length:
            text = text[:length]
        return text

    def format_time(self, seek, duration):
        play_time = str(datetime.timedelta(seconds=math.floor(int(seek)/1000)))
        
        if duration == 0:
            time_left = "Infinite"
        else:
            try:
                time_left = str(datetime.timedelta(seconds=int(duration)))
            except:
                time_left = "Unknown"
        
        return "{} / {}".format(play_time, time_left)

    def load_tiles(self):
        f = open('data.json')
        self.TILES = json.load(f)
        self.MAX_PAGES = math.ceil(len(self.TILES)/self.MAX_TILES)-1
        
        self.map_keys()

    def map_keys(self):
        p = self.PAGING if self.PAGING < self.MAX_PAGES else self.MAX_PAGES
        ps = p*self.MAX_TILES
        pe = (p+1)*self.MAX_TILES
        
        index = 0
        for tile in self.TILES[ps:pe]:
            index +=1
            self.render_key_img(tile["image"], tile["text"], self.OFFSET+index)
        
        for x in range(self.MAX_TILES-index):
            self.render_key_img("blank.png", "", self.OFFSET+index+x+1)