import os.path


# SCREEN CONFIGURATION
screen_width = 1000
screen_height = 800
screen_bg_color = (0, 100, 160)


# DIRECTORIES
dir_resources = 'resources'
dir_data = os.path.join(dir_resources, 'data')
dir_info = os.path.join(dir_resources, 'inf')
dir_font = os.path.join(dir_data, 'font')
dir_image = os.path.join(dir_data, 'img')


# FONTS
ubuntu_mono = 'Ubuntu Mono', 'UbuntuMono-R.ttf'
crysta = 'Crysta', 'Crysta.ttf'
fonts = ubuntu_mono, crysta

font_digital_clock = crysta[0]
font_default = ubuntu_mono[0]


# STYLE NAMES
style_card = 'card'
style_card_back = 'card back'
style_draw_deck = 'draw deck'
style_discard_deck = 'discard deck'
style_deck_bg = 'deck background'
style_clock_bg = 'clock background'
