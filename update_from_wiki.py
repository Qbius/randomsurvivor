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

def build_img_filename(basename):
    return f'''{imgs_dir}/{basename.replace("'", '').replace(':', '').replace(' ', '_').lower()}.png'''

def build_survivor_object(survivor_name):
    survivor_site = get_site(survivor_name)

    survivor_img = survivor_site.find('table', class_='infoboxtable').find('a').attrs['href']
    urlretrieve(survivor_img, build_img_filename(survivor_name))

    res = {}
    for skillbox in survivor_site.find_all('div', class_='skillbox'):
        slot_name = skillbox.find('div', class_='skilltype').text    
        skills = [(tb.find('tr').text.strip(), tb.find('a').attrs['href']) for tb in skillbox.find_all('table', class_='wikitable skill')]
        if survivor_name == 'MUL-T' and slot_name == 'Primary':
            res[slot_name] = [{'name': name, 'img': build_img_filename(name)} for name, _ in skills]
            res['Misc'] = [{'name': name, 'img': build_img_filename(name)} for name, _ in skills]

        elif survivor_name == 'Captain' and slot_name == 'Special':
            res[slot_name] = [{'name': name, 'img': build_img_filename(name)} for name, _ in skills[:1]]
            res['Misc1'] = [{'name': name, 'img': build_img_filename(name)} for name, _ in skills[1:]]
            res['Misc2'] = [{'name': name, 'img': build_img_filename(name)} for name, _ in skills[1:]]
        else:
            res[slot_name] = [{'name': name, 'img': build_img_filename(name)} for name, _ in skills]

        [urlretrieve(img_url, build_img_filename(name)) for name, img_url in skills]

    return {'img': build_img_filename(survivor_name), 'skills': res}


site = get_site('Survivors')
survivors = [name for div in site.find_all('div', class_='gallerytext') if (name := div.find('a').text) != 'Heretic']
survivors_info = json.dumps({survivor_name: build_survivor_object(survivor_name) for survivor_name in survivors}, indent=4)

with open('index.js', 'w') as output_file:
    output_file.write('const survivors = ' + survivors_info + """

const random_survivor = Object.entries(survivors)[Math.floor(Math.random() * Object.entries(survivors).length)];

let app = new Vue({
    el: '#app',
    data: {
        slot: '',
        choices: '',
        skill: '',

        chosen_survivor: random_survivor,
        chosen_skills: Object.fromEntries(Object.entries(random_survivor[1].skills).map(([slot, choices]) => [slot, Math.floor(Math.random() * choices.length)]))
    },
});
""")