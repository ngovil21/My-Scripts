from PIL import Image

import os
from lxml import html
import urllib.request

save_directory = 'C:\\Users\\Nikhil\\Downloads\\kingsofchaos'

base_url = 'http://www.kingsofchaos.com'
url = 'http://www.kingsofchaos.com/recruit.php?uniqid=yt524593'

image_prefix = "image_"

page = html.parse(url)
page_string = html.tostring(page, pretty_print=True)

print(page_string)

element = page.xpath("//form[@name='image_clickthrough_form']/p/img")

if not os.path.isdir(save_directory):
    os.makedirs(save_directory)
if not os.path.isdir(os.path.join(save_directory, "unsorted")):
    os.makedirs(os.path.join(save_directory, "unsorted"))

if element:
    image_src = element[0]
    index = 1
    file_name = image_prefix + "%03d.png" % index
    if os.path.exists(os.path.join(save_directory, file_name)):
        while os.path.exists(os.path.join(save_directory, file_name)):
            index += 1
            file_name = image_prefix + "%03d" % index
    urllib.request.urlretrieve(base_url + image_src, os.path.join(save_directory, "unsorted", file_name))
