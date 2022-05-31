import re
import requests
from tqdm import tqdm
from uuid import uuid4
from urllib.parse import urlparse

import_url = str(input("Url: "))

def download_file(url, name):
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    with open(name, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        raise Exception("ERROR, something wrong.")


template = re.compile("[a-z]{5}://[a-z]{0,10}\.[a-z]{0,10}\.[a-z]{0,3}/[a-z]/[a-zA-Z0-9]{0,40}/[a-z0-9]{0,10}/[^/)]{0,500}.[a-z0-9A-Z]{0,5}")
get_url_template = re.compile("http[s]{0,1}://[a-z]{5}\.[a-zA-Z]{0,10}\.[a-zA-Z]{2,3}/[^/')]{0,500}")
get_cur_font = lambda url: re.findall('[a-z]{0,10}://[a-zA-Z\.]{0,50}/[a-zA-Z]/[a-zA-Z0-9]{0,500}', url)[0].split('/')[-1]
get_families = re.compile('=[A-Z][a-z]{1,500}')
rendered_url = urlparse(import_url).query
list(map(lambda e:print(f"Detected font : {e}") ,list(map(lambda x: x[1:],get_families.findall( rendered_url)))))

url = get_url_template.search(import_url).group(0)

content_ = requests.get(url).content.decode()

urls = template.findall(content_)
new_content = ""

for url in urls:
    custom_uid = uuid4().__str__()[:4]
    download_file(f"{url[:-1]}", f"fonts/{get_cur_font(url[:-1])}{custom_uid}.woff2")
    print(get_cur_font(url[:-1]))
    content_ = content_.replace(url[:-1], f'fonts/{get_cur_font(url[:-1])}{custom_uid}.woff2')

with open("index.css", "w") as f:
    f.write(content_)
