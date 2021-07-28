from urllib.request import urlretrieve
from os.path import exists
import requests
import bs4
import os
import json

imgs_dir = 'images'
if not exists(imgs_dir):
    os.mkdir(imgs_dir)



def get_site(endpoint):
    return bs4.BeautifulSoup(requests.get(f'https://riskofrain2.fandom.com/wiki/{endpoint}').text, features='html.parser')

def build_img_filename(skill_name):
    return f'''{imgs_dir}/{skill_name.replace("'", '').replace(' ', '_').lower()}.png'''

def build_survivor_object(survivor_name):
    survivor_site = get_site(survivor_name)

    res = {}
    for skillbox in survivor_site.find_all('div', class_='skillbox'):
        slot_name = skillbox.find('div', class_='skilltype').text    
        skills = [(tb.find('tr').text.strip(), tb.find('a').attrs['href']) for tb in skillbox.find_all('table', class_='wikitable skill')]
        res[slot_name] = [{'name': name, 'img': build_img_filename(name)} for name, _ in skills]
        [urlretrieve(img_url, build_img_filename(name)) for name, img_url in skills]

    return res


site = get_site('Survivors')
survivors = [name for div in site.find_all('div', class_='gallerytext') if (name := div.find('a').text) != 'Heretic']
json.dump({survivor_name: build_survivor_object(survivor_name) for survivor_name in survivors}, open('survivors.json', 'w'), indent=4)