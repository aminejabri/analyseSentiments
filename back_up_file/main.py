from matplotlib import pyplot
import time
start_time = time.time()

from datetime import datetime


from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
#from vaderSentiment_fr.vaderSentiment import SentimentIntensityAnalyzer
import elasticsearch
import matplotlib.pyplot as plt
from elasticsearch import Elasticsearch
import twitter
import numpy as np

import json

from twitter.error import TwitterError

from lib.Translator import Translator

api = twitter.Api(consumer_key="oMzserpB6hwulRjXLAQpWaF06",
                  consumer_secret="kAlSeA8exYLa0MEbEqXCKjumo4LUpcUiPZX5fPmFrGbFaaAlyg",
                  access_token_key="1262371805601435654-dJJCVTU185qj0Ahg3cb7zUa2FTSwqP",
                  access_token_secret="VwSyZnp1IJKVQi3rK3AFJV43TKmNlqEePc1suvqbxEBGl")

# You can add to the client to apply to all requests
es = Elasticsearch("http://15.236.56.178:9200")
doc = {
        'size' : 10000,
        'query': {
            'match_all' : {}
       }
   }

# Or you can apply per-request for more granularity.
resp = es.search(index="original", body=doc)
hits = resp.get("hits").get("hits")

originalTweetsIds = set(filter(lambda x: x == 38395124,
                               list(map(lambda x: x.get("_source").get("user").get("id"), hits)))
                        )

originalTweetsIdsRetweeted = set(map(lambda x: x.get("_source").get("retweeted_status").get("id"),
                                        filter(lambda x: x.get("_source").get("retweeted_status"), hits)
                                        ))
originalTweetsIdsReplied = set(map(lambda x: x.get("_source").get("in_reply_to_status_id"),
                                   filter(lambda x: x.get("_source").get("in_reply_to_status_id"), hits)
                                   ))

originalTweetsIds = originalTweetsIds.union(originalTweetsIdsRetweeted)
originalTweetsIds = originalTweetsIds.union(originalTweetsIdsReplied)

structure = {}
x = 0
originalTweetsIds.remove(38395124)
for tweetId in originalTweetsIds:

    if tweetId not in structure:

        structure[tweetId] = {}

    dictOriginalTweets = structure[tweetId]

    if "responses" not in structure:
        dictOriginalTweets["responses"] = []
        dictOriginalTweets["retweeted_messages"] = []

    for hit in hits:
        if hit.get("_source").get("in_reply_to_status_id") and hit.get("_source").get("in_reply_to_status_id") == tweetId:

            dictOriginalTweets["responses"].append(hit.get("_source").get("text"))
            if "text" not in dictOriginalTweets:
                try:
                    in_reply_to_status_id = hit.get("_source").get("in_reply_to_status_id");
                    status = api.GetStatus(in_reply_to_status_id)
                    dictOriginalTweets["text"] = status.__getattribute__("text")
                except TwitterError:
                    print("Oops!  That was no valid number.  Try again...")
        elif hit.get("_source").get("retweeted_status") and hit.get("_source").get("retweeted_status").get("id") == tweetId:
            dictOriginalTweets["text"] = hit.get("_source").get("retweeted_status").get("text")

        elif hit.get("_source").get("is_quote_status") and hit.get("_source").get("quoted_status_id") == tweetId:
            dictOriginalTweets["text"] = hit.get("_source").get("quoted_status").get("text")
            dictOriginalTweets["retweeted_messages"].append(hit.get("_source").get("text"))

        elif hit.get("_source").get("id") == 38395124:
            dictOriginalTweets["text"] = hit.get("_source").get("text")

# function to print sentiments
# of the sentence.
def sentiment_scores(sentence):
    # Create a SentimentIntensityAnalyzer object.
    sid_obj = SentimentIntensityAnalyzer()

    # polarity_scores method of SentimentIntensityAnalyzer
    # oject gives a sentiment dictionary.
    # which contains pos, neg, neu, and compound scores.
    sentiment_dict = sid_obj.polarity_scores(sentence)

    print("Overall sentiment dictionary is : ", sentiment_dict)
    print("sentence was rated as ", sentiment_dict['neg'] * 100, "% Negative")
    print("sentence was rated as ", sentiment_dict['neu'] * 100, "% Neutral")
    print("sentence was rated as ", sentiment_dict['pos'] * 100, "% Positive")

    print("Sentence Overall Rated As", end=" ")

    # decide sentiment as positive, negative and neutral
    if sentiment_dict['compound'] >= 0.05:
        print("Positive")

    elif sentiment_dict['compound'] <= - 0.05:
        print("Negative")

    else:
        print("Neutral")

    return sentiment_dict


if __name__ == "__main__":
    print("\n1st statement :")
    sentence = "Geeks For Geeks is the best portal for \
    the computer science engineering students."

resultats_analyse = {}
i=0
for status_id in structure:

    """
    if "text" not in structure[status_id] or i == 2:
            break
            i = i+1
    """
    resultats_analyse[status_id] = {}
    responses = ' \n '.join(structure[status_id]["responses"])

    retweeted_messages = ' \n '.join(structure[status_id]["retweeted_messages"])

    translator = Translator()

    responses = translator.translate(responses, from_lang='fr', to_lang='en' )
    if len(responses) > 1000:
        x = len(responses)
    retweeted_message = translator.translate(responses, from_lang='fr', to_lang='en' )

    responses = responses + retweeted_message

    resultats_analyse[status_id]["sentiment"] = sentiment_scores(responses)
    resultats_analyse[status_id]["text"] = structure[status_id]["text"]

fileSimplified = []

for key in resultats_analyse:
    fileSimplified.append({"id":key,
                           "text": resultats_analyse[key]["text"],
                           "neg" :resultats_analyse[key]["sentiment"]['neg'],
                           "pos": resultats_analyse[key]["sentiment"]['pos'],
                           "neu": resultats_analyse[key]["sentiment"]['neu'],
                           })

with open('resultats_analyse.json', 'w') as fp:
    json.dump(fileSimplified, fp)

statistiques = {}
statistiques["nbr_tweet"] = len(structure)
statistiques["nbr_hits"] = len(hits)
statistiques["avg_rep"] = round(sum(map(lambda x : len(x["responses"]), structure.values()))/len(structure),2)
statistiques["avg_qtweet"] = round(sum(map(lambda x : len(x["retweeted_messages"]), structure.values()))/len(structure),2)
statistiques["duree_trmt"] = round(time.time() - start_time, 2)
statistiques["last_trmt"] = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

for x in resultats_analyse :
    if resultats_analyse[x]["sentiment"]['pos'] == max( map(lambda x: x["sentiment"]['pos'], resultats_analyse.values())):
        statistiques["max_pos"] = resultats_analyse[x]["text"]
        statistiques["id_max_pos"] = str(x)

        break
for x in resultats_analyse :
    if resultats_analyse[x]["sentiment"]['neg'] == max( map(lambda x: x["sentiment"]['neg'], resultats_analyse.values())):
        statistiques["max_neg"] = resultats_analyse[x]["text"]
        statistiques["id_max_neg"] = str(x)
        break
for x in resultats_analyse :
    if resultats_analyse[x]["sentiment"]['pos'] == min( map(lambda x: x["sentiment"]['pos'], resultats_analyse.values())):
        statistiques["min_pos"] = resultats_analyse[x]["text"]
        statistiques["id_min_pos"] = str(x)
        break
for x in resultats_analyse :
    if resultats_analyse[x]["sentiment"]['neg'] == min( map(lambda x: x["sentiment"]['neg'], resultats_analyse.values())):
        statistiques["min_neg"] = resultats_analyse[x]["text"]
        statistiques["id_min_neg"] = str(x)
        break

with open('statistiques.json', 'w') as fp:
    json.dump(statistiques, fp)

neg = sum(map(lambda x : x["sentiment"]['neg'], resultats_analyse.values()))/len(resultats_analyse)
pos = sum(map(lambda x : x["sentiment"]['pos'], resultats_analyse.values()))/len(resultats_analyse)
neu = sum(map(lambda x : x["sentiment"]['neu'], resultats_analyse.values()))/len(resultats_analyse)

labels = 'positive', 'neutre', 'négative'
sizes = [pos*100, neu*100, neg*100]
colors = ['yellowgreen', 'lightskyblue', 'lightcoral']

plt.pie(sizes, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=False, startangle=90)

plt.axis('equal')

plt.savefig('moyenne.png')
plt.show()

negMax = max( map(lambda x: x["sentiment"]['neg'], resultats_analyse.values()))
posMax = max( map(lambda x: x["sentiment"]['pos'], resultats_analyse.values()))
neuMax = max( map(lambda x: x["sentiment"]['neu'], resultats_analyse.values()))
negMin = min( map(lambda x: x["sentiment"]['neg'], resultats_analyse.values()))
posMin = min( map(lambda x: x["sentiment"]['pos'], resultats_analyse.values()))
neuMin = min( map(lambda x: x["sentiment"]['neu'], resultats_analyse.values()))
"""

negMax = 0.22
neuMax = 0.7
posMax = 0.11
negMin = 0.11
neuMin = 0.22
posMin = 0.77
labels = 'positive', 'neutre', 'négative'
"""

maxBar = plt.subplot()
maxBar.bar(range(3), [ posMax, neuMax,negMax], width = 0.5, color = 'red')
maxBar.set_title('les valeures max des penrcentages des sentiments')
maxBar.set_xticklabels(labels)
x = np.arange(len(labels))
maxBar.set_xticks(x)
for i in range(len( [ posMax, neuMax,negMax])):
    plt.text(x =  i - 0.15 , y =  [ posMax, neuMax,negMax][i] - [ posMax, neuMax,negMax][i]*2/3, s =  [ str(posMax), str(neuMax),str(negMax)][i], size = 12)

plt.savefig('max.png')
plt.cla()
minBar = plt.subplot()
minBar.bar(range(3), [ posMin, neuMin,negMin], width = 0.5, color = 'red')
minBar.set_title('les valeures min des penrcentages des sentiments')
minBar.set_xticklabels(labels)
x = np.arange(len(labels))
minBar.set_xticks(x)

for i in range(len( [ posMax, neuMax,negMax])):
    plt.text(x =  i - 0.15 , y =  [ posMin, neuMin,negMin][i] - [ posMin, neuMin,negMin][i]*2/3, s =  [ str(posMin), str(neuMin),str(negMin)][i], size = 12)

plt.savefig('min.png')
