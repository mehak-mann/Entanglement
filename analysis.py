import pandas as pd
import numpy as np
#import spacy
#import nltk
import datetime
from datetime import timedelta
#import Timedelta
#from nltk

def main():
    filename = "chatlog.csv"
    chat = pd.read_csv(filename)
    print(getNumberOfMessages(chat))
    print(getNumberOfResponses(chat))
    print(getAverageResponseTimes(chat))
    print(getNumberOfConversationsStarted(chat))
    print(getNumberOfWords(chat))
    print(getWords(chat))
    print(getCapsLockRatio(chat))

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
        if user is not prevUser:
            messageCount[user] += 1
        prevUser = user
    return messageCount

def getAverageResponseTimes(chat):
    '''
    Returns a mapping of users to their average reponse times to all other users
    *Includes responses to self
    '''
    original_chat = chat
    responseTimes = dict()
    chat['time'] = pd.to_datetime(chat['time'], infer_datetime_format=True)
    chat['time'] = chat['time'].diff()
    users = original_chat.user.unique()
    for user in users:
        user_chat = chat[chat['user'] == user]  # filters to only show messages sent by user
        responseTimes[user] = user_chat['time'].sum() / getNumberOfMessages(original_chat)[user]  # sums all response times and divides by total messages sent by user
    return responseTimes

def getNumberOfConversationsStarted(chat):
    '''
    Returns a mapping of users to the number of conversations they've started,
    assuming a 12-hour gap signifies the start of a new conversation
    '''
    conversationsStarted = dict()
    conversationsStarted[chat['user'][0]] = 1  # automatically setting very first message's user to 1
    chat['time'] = pd.to_datetime(chat['time'], infer_datetime_format=True)
    chat = chat[chat['time'].diff() > Timedelta.to_timedelta64('12:00:00.00')]
    for index in chat.index:
        user = text['user'][index]
        if user not in conversationsStarted.keys():
            conversationsStarted[user] = 0
        conversationsStarted[user] += 1
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
    Returns a mapping of users to the number of words they sent
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
    capsRatio = dict()
    for index in chat.index:
        user = chat['user'][index]
        if user not in capsRatio.keys():
            capsRatio[user] = 0
        words = chat['message'][index].split() # split the message into an array of words
        for word in words:
            if isCapsLock(word) and len(word) > 1:
                capsRatio[user] =+ 1
            
    return capsRatio

def isCapsLock(word):
    for char in word:
        if char.islower():
            return False
    return True  

if __name__ == '__main__':
    main()

# --------------------------------------- Helper methods -----------------------------------
