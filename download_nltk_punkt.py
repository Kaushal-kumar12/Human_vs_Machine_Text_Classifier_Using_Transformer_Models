import nltk


nltk.download('punkt_tab')

from nltk.tokenize import sent_tokenize

text = "Hello, How are you today?"
sentences = sent_tokenize(text)
print(sentences)
