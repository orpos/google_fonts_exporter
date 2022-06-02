import re
import sys

from time import sleep
import requests

try:
    from tqdm import tqdm
except ImportError:
    tqdm_available = False
    tqdm = None
else:
    tqdm_available = True

from uuid import uuid4
from urllib.parse import urlparse

utf8_or_more_support = True

if len(sys.argv) > 1:
    import_url = sys.argv[1]
else:
    import_url = str(input("Url: "))


def download_file(url, name):
    r = session.get(url, stream=True)
    total = int(r.headers.get('content-length', 0))
    if tqdm_available:
        with open(name, 'wb') as file, tqdm(
                desc=name,
                total=total,
                unit='iB',
                unit_scale=True,
                unit_divisor=2048,
        ) as bar:
            for data in r.iter_content(chunk_size=2048):
                size = file.write(data)
                bar.update(size)
                sleep(0.01)
    else:
        with open(name, 'wb') as file:
            for data in r.iter_content(chunk_size=2048):
                file.write(data)
                print(data.hex().upper()[:16])
                sleep(0.01)
            print(f'{name} Downloaded')


session = requests.Session()
if utf8_or_more_support:
    session.headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/102.0.0.0 '
                      'Safari/537.36',  # I putted this because it seems to import more special fonts like languages
        # that had other character that is not in abc
    }

# Find the urls in the main css file
template = re.compile(
    r"[a-z]{0,5}://[a-z]{0,10}\.[a-z]{0,10}\.[a-z]{0,3}/[a-z]/[a-zA-Z0-9]{0,40}/[a-z0-9]{0,10}/[^/)]{0,500}.[a-z0-9A-Z]{0,5}")
# Render the link from the input (filter the link)
get_url_template = re.compile(r"http[s]{0,1}://[a-z]{5}\.[a-zA-Z]{0,10}\.[a-zA-Z]{2,3}/[^/')]{0,500}")
# Render the font link when iterating the links
get_cur_font = lambda url: re.findall(r"/[a-zA-Z]/[^/]{0,100}", url)[0].replace('/s/', '')
# Render the name of the families imported in the css
get_families = re.compile(r'=[A-Za-z]{1}[(A-Za-z+^&:)]{0,200}')
# Render the url to be less difficult to get the families
rendered_url = urlparse(import_url).query
# Filter the fonts from the url
fonts = list(
    map(
        lambda x: x.replace('+', ' '),  # Replace the + from the link to be spaces
        map(
            lambda x: re.findall(r'[A-Za-z+]{0,60}', x)[1],
            get_families.findall(rendered_url)[:-1]
        )
    )
)
if len(fonts) < 1:
    print("ERROR: No fonts detected! ")
    sys.exit(1)
# Print the available fonts (I made that way to take less space in the code)
list(map(lambda x: print("Detected Font: %s" % x), fonts))
choice = str(input("Proceed [Y]?")).upper()
if choice == 'N':
    sys.exit(0)

# Get the link from input
url = get_url_template.search(import_url).group(0)

# Get the css file
content_ = session.get(url).content.decode()

# Get all the urls in it
urls = template.findall(content_)
new_content = ""

for url in urls:
    custom_uid = uuid4().__str__()[:4]  # Generate some random text to put in front of file to don't have files with
    # same name
    download_file(f"{url[:-1]}", f"fonts/{get_cur_font(url[:-1])}{custom_uid}.woff2")
    # Change the url in the css
    content_ = content_.replace(url[:-1], f'fonts/{get_cur_font(url[:-1])}{custom_uid}.woff2')

with open("index.css", "w") as f:
    f.write(content_)  # Write it to the index.css

print('Done!')
input('Press enter to see index.css')
print(content_)
