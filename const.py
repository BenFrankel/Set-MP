import os.path


# FILE SYSTEM
# - Resources
dir_resources = 'resources'
dir_data = os.path.join(dir_resources, 'data')
dir_info = os.path.join(dir_resources, 'info')
dir_font = os.path.join(dir_data, 'font')
dir_image = os.path.join(dir_data, 'img')

# - User Data
dir_user_data = 'userdata'
dir_friend_data = os.path.join(dir_user_data, 'friends')


# RESOURCES TODO: Find resources automatically from a data file.
# - FONTS
ubuntu_mono = 'Ubuntu Mono', 'UbuntuMono-R.ttf'
crysta = 'Crysta', 'Crysta.ttf'
fonts = ubuntu_mono, crysta

font_digital_clock = crysta[0]
font_default = ubuntu_mono[0]

# - IMAGES
images = tuple()
