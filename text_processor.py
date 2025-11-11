import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import string

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

def preprocess_text(text):
    
    lemmatizer = WordNetLemmatizer()
    
    stop_words = set(stopwords.words('english'))
    
    tokens = word_tokenize(text.lower())
    
    processed_tokens = [
        lemmatizer.lemmatize(token) 
        for token in tokens 
        if token not in stop_words and token not in string.punctuation
    ]
    
    processed_text = ' '.join(processed_tokens)
    
    return processed_text
