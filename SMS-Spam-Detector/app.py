import streamlit as st
import pickle
import nltk
from nltk.corpus import stopwords
import string
from nltk.stem.porter import PorterStemmer

nltk.download('punkt_tab')
nltk.download('punkt')
custom_stopwords = {
    "i","me","my","myself","we","our","ours","ourselves","you","your","yours",
    "yourself","yourselves","he","him","his","himself","she","her","hers",
    "herself","it","its","itself","they","them","their","theirs","themselves",
    "what","which","who","whom","this","that","these","those","am","is","are",
    "was","were","be","been","being","have","has","had","having","do","does",
    "did","doing","a","an","the","and","but","if","or","because","as","until",
    "while","of","at","by","for","with","about","against","between","into",
    "through","during","before","after","above","below","to","from","up","down",
    "in","out","on","off","over","under","again","further","then","once","here",
    "there","when","where","why","how","all","any","both","each","few","more",
    "most","other","some","such","no","nor","not","only","own","same","so",
    "than","too","very","s","t","can","will","just","don","should","now"
}

tfidf = pickle.load(open('vectorizer.pkl', 'rb'))
model = pickle.load(open('model.pkl', 'rb'))

ps = PorterStemmer()
def transform_text(text):
    # lowering the text
    text = text.lower()
    # tokenizing the text and convert the list
    text_list = nltk.word_tokenize(text)
    # remove special characters
    rem_sp_ch = []
    # remove stop words
    rem_stop_words = []
    for item in text_list:
        if item.isalnum():
            rem_sp_ch.append(item)
            
    for item in rem_sp_ch:
        if item not in custom_stopwords and item not in string.punctuation:
            rem_stop_words.append(item)

       #  Stemming the data
    clean_data = [ps.stem(item) for item in rem_stop_words ]
    return " ".join(clean_data)

st.set_page_config(page_title="Spam Detector", layout="wide", initial_sidebar_state="expanded")
st.title('SMS/Email Spam Detector')

msg = st.text_area(
"Enter SMS / Email text",
height=150,
placeholder="Enter Your SMS or Email text here..."
)
# 1. preprocess
transforms_sms = transform_text(msg)
#  2. vectorize
vectorized_sms = tfidf.transform([transforms_sms]).toarray()
#  3. predict
result = model.predict(vectorized_sms)[0]
# 4. display result
if st.button('Predict'):
    if result == 1:
        st.header('Spam')
    else:
        st.header('Not Spam')







