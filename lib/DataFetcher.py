from elasticsearch import Elasticsearch
import json
import requests


class DataFetcher:

    def __init__(self, url="http://15.236.56.178", port="9200", index="original", urlSuffixe="/_search"):
        self.url = url
        self.port = port
        self.index = index
        self.urlSuffixe = urlSuffixe
        full_path = self.url + ":" + self.port
        self.elastic = Elasticsearch(full_path)
        self.search_param = {}

    def fetchFromElastic(self, index):
        return self.elastic.search(index="original", body="")

    def format(self, data):
        return

    def setFilter(self, filters):
        pass

    def setDefaultFilter(self):
        self.search_param = {
            "query": {
                "terms": {
                    "_id": [1234, 42]
                }
            }
        }
