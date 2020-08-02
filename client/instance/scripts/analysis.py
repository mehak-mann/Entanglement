import pandas as pd
import numpy as np
from gensim.summarization import keywords
import spacy
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
stopwords = set(stopwords.words('english'))
from spacy.lang.en import English
nlp = English()
nlp.max_length = 10000000
from textblob import TextBlob
import datetime
from datetime import timedelta
# import matplotlib.pyplot as plt
# import matplotlib
# import seaborn as sns
import json


def main(filename, filetype):
    #return run(filename, filetype)

     # converts data into pd dataframe
    chatlog = getChat(filename, filetype)

    # create all visualizations
    # createPlots(chatlog)    # doesn't work with UI yet

    # fetch statistics
    return fetchStatistics(chatlog)

def getChat(filename, filetype):
    '''
    Takes a filename and a type, where type is either 'json' or 'csv'
    '''
    # fetches data and converts to pd dataframe

    if filetype == 'json':
        return spawnDF(filename)
    elif filetype == 'csv':
        chat = pd.read_csv(filename)
        chat['time'] = pd.to_datetime(chat['time'], infer_datetime_format=True)
        return chat

def createPlots(chat):
    '''
    Fetches visualizations of data.
    '''
    # plots messages per person over time (bar graph)
    messages = getNumberOfMessages(chat)
    plotMessages(messages)
    plt.close()
    # plots conversations started per person over time (bar graph)
    convosStarted = getNumberOfConversationsStarted(chat)
    plotConvosStarted(convosStarted)
    plt.close()
    # plots words sent per person over time (line graph)
    plotWordsOverTime(chat)
    plt.close()
    # plots response time per person over time (line graph)
    plotResponseTimeOverTime(chat)
    plt.close()
    # plots sentiment per person over time (line graph)
    plotSentimentOverTime(chat)
    plt.close()

def fetchStatistics(chat):
    '''
    Fetches statistics for data.
    '''
    numberOfMessages = getNumberOfMessages(chat)     # dict of total number of messages per person
    numberOfResponses = getNumberOfResponses(chat)      # dict of total number of response-messages per person
    averageResponseTimes = getAverageResponseTimes(chat)      # dict of average response times per person
    conversationsStarted = getNumberOfConversationsStarted(chat)     # dict of total number of conversations started per person (12 hr gap)
    numberOfWords = getNumberOfWords(chat)     # dict of total number words sent per person
    capsLockRatio = getCapsLockRatio(chat)     # dict of capslock ratio per person
    userSentiment = getUserSentiment(chat)     # dict of sentiment per person
    userKeywords = userKeyWords(chat)          # dict of most popular words/phrases per person
    conversationSentiment = getConversationSentiment(chat)     # integer holistic conversation sentiment
    result = [numberOfMessages, numberOfResponses, averageResponseTimes, conversationsStarted, numberOfWords,
    capsLockRatio, userSentiment, userKeywords, conversationSentiment]
    return result

# -------------------------------- Statistics --------------------------------

def getNumberOfMessages(chat):
    '''
    Returns a mapping of users to the number of messages they sent
    '''
    messageCount = dict()
    for index in chat.index:
        user = chat['user'][index]
        if user not in messageCount.keys():
            messageCount[user] = 0
        messageCount[user] += 1
    return messageCount

def getNumberOfResponses(chat):
    '''
    Returns a mapping of users to how many times they respond (not including sequences of messages by same user)
    '''
    messageCount = dict()
    prevUser = None
    for index in chat.index:
        user = chat['user'][index]
        if user not in messageCount.keys():
            messageCount[user] = 0
        if user is not prevUser and prevUser is not None:
            messageCount[user] += 1
        prevUser = user
    return messageCount

def getTotalResponseTimes(chat):
    '''
    Returns a mapping of users to the total response times
    '''
    totalResponseTimes = dict()
    prevUser = None
    
    for index in chat.index:
        user = chat['user'][index]
        if user not in totalResponseTimes.keys():
            totalResponseTimes[user] = pd.to_timedelta('00:00:00.00')
        if user is not prevUser and prevUser is not None:
            totalResponseTimes[user] += chat['time'][index] - chat['time'][index-1]
        prevUser = user
    return totalResponseTimes

def getAverageResponseTimes(chat):
    '''
    Returns a mapping of users to their average reponse times to all other users
    '''
    responseTimes = dict()
    changed_chat = chat[:]
    changed_chat['time'] = changed_chat['time'].diff()
    numResponses = getNumberOfResponses(chat)
    totalResponseTimes = getTotalResponseTimes(chat)
    users = chat.user.unique()
    for user in users:
        user_chat = changed_chat[changed_chat['user'] == user]  # filters to only show messages sent by user
        responseTimes[user] = totalResponseTimes[user] / numResponses[user]  # sums all response times and divides by total messages sent by user
    return responseTimes

def getResponseTimes(chat):
    '''
    Returns a dataframe of message names and response times over time
    '''
    responseTimes = dict()
    changed_chat = chat[:]
    changed_chat['time'] = changed_chat['time'].diff()
    return changed_chat

def getNumberOfConversationsStarted(chat):
    '''
    Returns a mapping of users to the number of conversations they've started,
    assuming a 12-hour gap signifies the start of a new conversation
    '''
    new_chat = chat[:]
    conversationsStarted = dict()
    conversationsStarted[new_chat['user'][0]] = 1  # automatically setting very first message's user to 1
    new_chat = new_chat[new_chat['time'].diff() > pd.to_timedelta('12:00:00.00')]
    for index in new_chat.index:
        user = new_chat['user'][index]
        if user not in conversationsStarted.keys():
            conversationsStarted[user] = 0
        conversationsStarted[user] += 1
    for user in chat.user.unique():
        if user not in conversationsStarted.keys():
            conversationsStarted[user] = 0
    return conversationsStarted

def getNumberOfWords(chat):
    '''
    Returns a mapping of users to the number of words they sent
    '''
    wordRatio = dict()
    for index in chat.index:
        user = chat['user'][index]
        if user not in wordRatio.keys():
            wordRatio[user] = 0
        words = chat['message'][index].split() # split the message into an array of words
        wordRatio[user] += len(words) # count words and add to user's count of words
    return wordRatio

def getWords(chat):
    '''
    Returns a mapping of users to the words they sent
    '''
    words = dict()
    for index in chat.index:
        user = chat['user'][index]
        if user not in words.keys():
            words[user] = []
        curr_words = chat['message'][index].split() # split the message into an array of words
        words[user].extend(curr_words) # append words to user's words
    return words

def getCapsLockRatio(chat):
    '''
    Returns a mapping of users to their caps lock ratios
    '''
    capsRatio = dict()
    allWords = getWords(chat)
    for user in allWords.keys():
        capsRatio[user] = 0
        words = allWords[user]# split the message into an array of words
        for word in words:
            if isCapsLock(word) and len(word) > 1:
                capsRatio[user] += 1

def isCapsLock(word):
    for char in word:
        if char.islower():
            return False
    return True

def getConversationSentiment(chat):
    '''
    Function to return sentiment score between -1 to 1 for total sentiment
    '''
    totalWords = []
    words = getWords(chat)
    for user in words.keys():
        totalWords.extend(words[user])
    return TextBlob(' '.join(totalWords)).sentiment.polarity

def getUserSentiment(chat):
    '''
    Function to return sentiment score between -1 to 1 for each person.
    '''
    sentiments = dict()
    words = getWords(chat)
    for user in words.keys():
        sentiments[user] = TextBlob(' '.join(words[user])).sentiment.polarity
    return sentiments

def getMessageSentiment(chat):
    '''
    Function to return sentiment score between -1 to 1 for each message.
    '''
    added_sentiment = chat.copy(deep=True)
    added_sentiment['sentiment'] = added_sentiment['message'].apply(lambda x: TextBlob(x).sentiment.polarity)
    return added_sentiment

def preprocess(text):
    # Create Doc object
    doc = nlp(text, disable=['ner', 'parser'])
    # Generate lemmas
    lemmas = [token.lemma_ for token in doc]
    #Remove stopwords and non-alphabetic characters
    a_lemmas = [lemma for lemma in lemmas
            if lemma.isalpha() and lemma not in stopwords]
    
    return ' '.join(a_lemmas)

def userKeyWords(chat):
    '''
    Function to return key words for each person.
    '''
    userKeyWords = dict()
    words = getWords(chat)
    for user in words.keys():
        values = keywords(text=preprocess(' '.join(words[user])),split='\n')
        userKeyWords[user] = values[:10]
    try:
        return userKeyWords
    except:
        return "no content"

# -------------------------------- Visualizations --------------------------------

# def plotMessages(messages):
#     names = list(messages.keys())
#     number = list(messages.values())
#     df = pd.DataFrame(list(zip(names, number)), columns=['Person', 'Number of Messages'])
#     sns.set(style="whitegrid")
#     sns.barplot(x="Person", y="Number of Messages", data=df).set_title("Number of Messages per Person")
#     plt.savefig("Visualizations/Number of Messages per person.jpeg")

# def plotConvosStarted(convoStarted):
#     names = list(convoStarted.keys())
#     number = list(convoStarted.values())
#     df = pd.DataFrame(list(zip(names, number)), columns=['Person', 'Number of Conversations Started'])
#     sns.set(style="whitegrid")
#     sns.barplot(x="Person", y="Number of Conversations Started", data=df).set_title("Number of Conversations Started per Person")
#     plt.savefig("Visualizations/Conversations Started per Person.jpeg")

# def plotResponseTimeOverTime(chat):
#     '''
#     Message words over time
#     '''
#     changed_chat = getResponseTimes(chat)
#     changed_chat['time'] = changed_chat['time'].dt.seconds
#     users = chat.user.unique()
#     sns.set(style="whitegrid")
#     for user in users:
#        user_chat = changed_chat[changed_chat['user'] == user]
#        plt.plot(user_chat['time'], label=user)
#     plt.legend(loc='lower left')
#     plt.xlabel("Time")
#     plt.ylabel("Response Time (s)")
#     plt.title("Response Times per Person (over Time)")
#     plt.savefig("Visualizations/Response Times per Person (over Time).jpeg")

# def plotWordsOverTime(chat):
#     '''
#     Message words over time
#     '''
#     changed_chat = chat[:]
#     changed_chat['message'] = changed_chat['message'].apply(lambda x: len(x.split()))
#     users = chat.user.unique()
#     sns.set(style="whitegrid")
#     for user in users:
#        user_chat = changed_chat[changed_chat['user'] == user]
#        plt.plot(user_chat['message'], label=user)
#     plt.legend(loc='lower left')
#     plt.xlabel("Time")
#     plt.ylabel("Words per Message")
#     plt.title("Words per Message Over Time")
#     plt.savefig("Visualizations/Words per Message Over Time.jpeg")

# def plotSentimentOverTime(chat):
#     '''
#     Sentiment over time
#     '''
#     changed_chat = getMessageSentiment(chat)
#     users = chat.user.unique()
#     sns.set(style="whitegrid")
#     for user in users:
#        user_chat = changed_chat[changed_chat['user'] == user]
#        plt.plot(user_chat['sentiment'], label=user)
#     plt.legend(loc='lower left')
#     plt.xlabel("Time")
#     plt.ylabel("Sentiment Score (Scale -1 to 1)")
#     plt.title("Sentiment per Person over Time")
#     plt.savefig("Visualizations/Sentiment per Person over Time.jpeg")

# -------------------------------- Converts chatlog to program-readable format --------------------------------

def fix_text_encoding(text):
    '''
    Fixes text encoding, see https://stackoverflow.com/questions/50008296/facebook-json-badly-encoded
    '''
    return text.encode('latin1').decode('utf8')

def spawnDF(filename):
    data = []
    with open(filename, encoding="utf8") as f:
        json_data = json.load(f)
    for message in json_data["messages"]:
        timestamp = datetime.datetime.fromtimestamp(int(message['timestamp_ms']/1000))
        tm = timestamp
        timestamp -= datetime.timedelta(microseconds=tm.microsecond)
        if "content" in message and "sender_name" in message:
            content = fix_text_encoding(message["content"])
        if "sender_name" in message:
            sender_name = fix_text_encoding(message["sender_name"])
        data += [[sender_name, timestamp, content]]
    df = pd.DataFrame(data, columns=['user', 'time', 'message'])
    df = df.iloc[::-1]    
    df.index = range(len(df.index))
    print(df)
    return df