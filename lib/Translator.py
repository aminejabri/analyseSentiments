import json
import requests


class Translator:

    @staticmethod
    def translate(sentence, from_lang='fr', to_lang='en'):
        api_url = "http://mymemory.translated.net/api/get?q={}&langpair={}|{}".format(sentence, from_lang, to_lang)
        hdrs = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'
        }
        response = requests.get(api_url, headers=hdrs)
        response_json = json.loads(response.text)
        return response_json["responseData"]["translatedText"]
