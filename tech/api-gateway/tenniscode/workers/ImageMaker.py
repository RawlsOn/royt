import io, time, os, glob, pprint, json, re, shutil, ntpath, csv
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from django.db.models import Avg, Case, Count, F, Max, Min, Prefetch, Q, Sum, When

# from copy import copy
from datetime import datetime, date, timedelta
from common.util.str_util import print_progress

from PIL import Image,ImageDraw,ImageFont
import random

pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

class ImageMaker(object):

    def __init__(self, args={}):
        self.args = args

        self.outdir = '/usr/data/LOVE_TENNIS/images'

    def run(self, text):
        print('run ImageMaker', self.args)
        print(text)

        draw_text = text
        text_count = len(draw_text)

        BG_COLORS = [ 'B71C1C', '880E4F', '4A148C', '311B92', '1A237E', '0D47A1', '01579B', '006064', '004D40', '1B52E0', '33691E', '827717', 'F57F17', 'FF6F00', 'E65100', 'BF360C', '3E2723', '212121', '263238' ]

        IMG_WIDTH = 1200
        IMG_HEIGHT = 1200
        LEFT_MARGIN = 50
        RIGHT_MARGIN = 50
        FONT_SIZE = int((IMG_WIDTH - LEFT_MARGIN - RIGHT_MARGIN) / text_count)
        font = ImageFont.truetype("/usr/data/LOVE_TENNIS/resources/fonts/SUIT-Variable-ttf/SUIT-Variable.ttf", FONT_SIZE)
        font.set_variation_by_name('Bold')
        # 이미지 사이즈 지정

        canvas = Image.new('RGB', (IMG_WIDTH, IMG_HEIGHT), color='#' + random.choice(BG_COLORS))

        draw = ImageDraw.Draw(canvas)
        w, h = font.getsize(draw_text)
        draw.text(
            (
                (IMG_WIDTH-w) / 2.0,
                (IMG_HEIGHT-h) / 2.0
            ),
            draw_text, 'white', font
        )

        # png로 저장 및 출력해서 보기
        canvas.save('/usr/data/LOVE_TENNIS/images/' + text + '.png', "PNG")
        canvas.show()