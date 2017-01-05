import os.path


# WINDOW CONFIGURATION
window_w = 1000
window_h = 800
window_bgcolor = (0, 100, 160)


# FILE SYSTEM
dir_resources = 'resources'
dir_data = os.path.join(dir_resources, 'data')
dir_info = os.path.join(dir_resources, 'inf')
dir_font = os.path.join(dir_data, 'font')
dir_image = os.path.join(dir_data, 'img')


# RESOURCES TODO: Find resources automatically from a data file.
# - FONTS
ubuntu_mono = 'Ubuntu Mono', 'UbuntuMono-R.ttf'
crysta = 'Crysta', 'Crysta.ttf'
fonts = ubuntu_mono, crysta

font_digital_clock = crysta[0]
font_default = ubuntu_mono[0]

# - IMAGES
images = tuple()


# STYLE NAMES
# - SETGAME
style_card = 'card'
style_card_back = 'card back'
style_draw_deck = 'draw deck'
style_discard_deck = 'discard deck'
style_deck_bg = 'deck background'
style_clock_bg = 'clock background'

# - GENERAL
style_button = 'button'
style_default_font = 'default font'
