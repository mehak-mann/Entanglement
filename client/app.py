import os
from flask import Flask
from flask import render_template
from flask import request
from instance.scripts.analysis import main

app = Flask(__name__)

uploads_dir = os.path.join(app.instance_path, 'scripts')

app.config['FLASK_APP'] = 'app'
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.config['TESTING'] = True

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/charts')
def charts():
    return render_template('charts.html')

@app.route('/chartsm')
def chartsm():
    return render_template('charts-matt.html')

@app.route('/get_data', methods=['POST'])
def get_data():
    dataFile = request.files['file_path']
    dataFileName = dataFile.filename
    dataFile.save(os.path.join(uploads_dir, dataFileName))

    if "csv" in dataFileName:
        fileType = "csv"
    
    if "json" in dataFileName:
        fileType = "json"

    if "matt" in dataFileName:
        which_url = "/chartsm"
    else:
        which_url ="/charts"
    filePath = 'scripts/' + dataFileName
    result = main(os.path.join(app.instance_path, filePath), fileType)

    numberOfMessages = result[0]
    numberOfResponses = result[1]
    averageResponseTimes = result[2]
    conversationsStarted = result[3]
    numberOfWords = result[4] 
    # capsLockRatio = result[5]
    userSentiment = result[6]           
    userKeywords = result[7]                   
    conversationSentiment = result[8]
    
    if (conversationSentiment < -0.25):
        sentiment = "toxic. Try harder to get along with this person."
        overallSent = "😠"
    elif (conversationSentiment > 0.25):
        sentiment = "healthy. You are great friends!"
        overallSent = "😊"
    else:
        sentiment = "neutral. This may indicate that the conversation didn't have much value. There could have been a mix of positive and negative emotions."
        overallSent = "😐"

    aRT=averageResponseTimes
    aRTKeys=list(averageResponseTimes.keys())
    aRTLeft=aRT[aRTKeys[0]]
    aRTRight=aRT[aRTKeys[1]]
    secondsLeft = aRTLeft.seconds
    secondsRight = aRTRight.seconds
    aRTLeft=[aRTLeft.days, secondsLeft//3600, (secondsLeft//60)%60, secondsLeft%60]
    aRTRight=[aRTRight.days, secondsRight//3600, (secondsRight//60)%60, secondsRight%60]
    aRTLeftStr = "{} days {} hr {} min {} secs".format(aRTLeft[0], aRTLeft[1], aRTLeft[2], aRTLeft[3])
    aRTRightStr = "{} days {} hr {} min {} secs".format(aRTRight[0], aRTRight[1], aRTRight[2], aRTRight[3])

    return render_template('analysis.html', nM=numberOfMessages, nMKeys=list(numberOfMessages.keys()), 
                                            nR=numberOfResponses, nRKeys=list(numberOfResponses.keys()),
                                            cS=conversationsStarted, cSKeys=list(conversationsStarted.keys()),
                                            aRTKeys=aRTKeys, aRTLeft=aRTLeftStr, aRTRight=aRTRightStr,
                                            nW=numberOfWords, nWKeys=list(numberOfWords.keys()),
                                            #cLR=capsLockRatio, cLRKeys=list(capsLockRatio.keys()),
                                            uS=userSentiment, uSKeys=list(userSentiment.keys()),
                                            uK=userKeywords, uKKeys=list(userKeywords.keys()), 
                                            cSe=conversationSentiment, sentiment=sentiment, overallSent=overallSent,
                                            which_url=which_url
                            )

if __name__ == "__main__":
    app.run(debug=True)