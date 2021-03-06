'''from flask import Flask, render_template
from flask import Flask, render_template, request
from wtforms import Form, TextAreaField, validators


app = Flask(__name__)
class HelloForm(Form):
    sayhello = TextAreaField('',[validators.DataRequired()])
@app.route('/')
def index():
    form = HelloForm(request.form)
    return render_template('first_app.html', form=form)
@app.route('/hello', methods=['POST'])
def hello():
    form = HelloForm(request.form)
    if request.method == 'POST' and form.validate():
        name = request.form['sayhello']
        return render_template('hello.html', name=name)
    return render_template('first_app.html', form=form)
if __name__ == '__main__':
    app.run(debug=True)'''


from flask import Flask, render_template, request
from wtforms import Form, TextAreaField, validators
import pickle
import sqlite3
import os
import numpy as np


# import HashingVectorizer from local dir
from sklearn.feature_extraction.text import HashingVectorizer
import re
from nltk.corpus import stopwords
#import nltk
#nltk.download('stopwords')

def tokenizer(text):
    text = re.sub('<[^>]*>', '', text)
    emoticons = re.findall('(?::|;|=)(?:-)?(?:\)|\(|D|P)',
                           text.lower())
    text = re.sub('[\W]+', ' ', text.lower()) \
                   + ' '.join(emoticons).replace('-', '')
    tokenized = [w for w in text.split() if w not in stop]
    return tokenized

vect = HashingVectorizer(decode_error='ignore',
                         n_features=2**21,
                         preprocessor=None,
                         tokenizer=tokenizer)
stop = open("english", "r")


#------------------------------------------------------------------------------------------------


app = Flask(__name__)

######## Preparing the Classifier
cur_dir = os.path.dirname(__file__)
clf = pickle.load(open(os.path.join(cur_dir,
                 'pkl_objects/classifier.pkl'), 'rb'))
db = os.path.join(cur_dir, 'reviews.sqlite')


def classify(document):
    label = {0: 'negative', 1: 'positive'}
    X = vect.transform([document])
    y = clf.predict(X)[0]
    proba =  clf.predict_proba(X).max()
    return label[y], proba

def train(document, y):
    X = vect.transform([document])
    clf.partial_fit(X, [y])



def sqlite_entry(path, document, y):
       conn = sqlite3.connect(path)
       c = conn.cursor()
       c.execute("INSERT INTO review_db (review, sentiment, date)"\
       " VALUES (?, ?, DATETIME('now'))", (document, y))
       conn.commit()
       conn.close()

#------------------------------------------------------------------------------------------------

application = Flask(__name__)
class ReviewForm(Form):
   moviereview = TextAreaField('',
                               [validators.DataRequired(),
                               validators.length(min=15)])
@application.route('/')
def index():
   form = ReviewForm(request.form)
   return render_template('reviewform.html', form=form)
@application.route('/results', methods=['POST'])
def results():
   form = ReviewForm(request.form)
   if request.method == 'POST' and form.validate():
       review = request.form['moviereview']
       y, proba = classify(review)
       return render_template('results.html',
                               content=review,
                               prediction=y,
                               probability=round(proba*100, 2))
   return render_template('reviewform.html', form=form)
@application.route('/thanks', methods=['POST'])
def feedback():
   feedback = request.form['feedback_button']
   review = request.form['review']
   prediction = request.form['prediction']
   inv_label = {'negative': 0, 'positive': 1}
   y = inv_label[prediction]
  # if feedback == 'Incorrect':
 #      y = int(not(y))
  # train(review, y)
 #  sqlite_entry(db, review, y)
   return render_template('thanks.html')

#if __name__ == '__main__':
#  application.run(host="0.0.0.0",port=8080,debug=True)
#  application.run(debug=True)       


if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()










