import json
import os
import pandas as pd
from lxml import etree
import re

CURRENT_DIR = os.path.dirname(__file__)

def main():
    print("Localizing...")
    with open(os.path.join(CURRENT_DIR, "settings.json")) as setting_file:
        setting = json.load(setting_file)

        IN_PATH = setting["IN_PATH"]
        OUT_PATH = setting["OUT_PATH"]
        LANG_KEYS = setting["LANGUAGES"]
        CSV = setting["FILE"]

        print("In path: {0}".format(IN_PATH))
        print("Out path: {0}".format(OUT_PATH))
        print("Lang keys: {0}".format(LANG_KEYS))
        print("------------------------------------\nSTART...")

        localize_android(CURRENT_DIR, OUT_PATH, LANG_KEYS, CSV)

        print('DONE LOCALIZING.\n')


def localize_android(BASE_PATH, OUT_PATH, LANG_KEYS, CSV):
    data = pd.read_csv(CSV)
    features = data['Feature String ID'].tolist()

    os.chdir('../../')
    path = os.getcwd() + OUT_PATH
    base_out_dir = os.path.join(BASE_PATH, path)
    if not os.path.exists(base_out_dir):
        os.makedirs(base_out_dir)

    for lang in LANG_KEYS:
        lang_id = lang['id']
        lang_aliases = lang['alias']

        folder = base_out_dir
        if lang_id != "en":
            folder += "-" + lang_id
        if not os.path.exists(folder):
            os.makedirs(folder)

        # last alias mentioned in [lang_aliases] variable has highest priority
        for alias in lang_aliases:
            translations = data[alias].tolist()
            assert len(translations) == len(features)

            resource = etree.Element("resources")
            for i in range(0, len(translations)):
                feature = str(features[i])
                translation = str(translations[i])

                item = etree.SubElement(resource, "string")
                item.set('name', feature)
                item.text = re.sub('(%\d)', "\\1$s", translation.replace("'", "\\'"))

            with open(os.path.join(folder, "strings.xml"), "wb") as out_file:
                out_file.write(etree.tostring(resource, xml_declaration=True, pretty_print=True,
                                              encoding="utf-8"))
                out_file.close()

if __name__ == '__main__':
    main()
