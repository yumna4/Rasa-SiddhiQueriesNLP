import nltk
sentences = nltk.sent_tokenize("for each temperature")
sentences = [nltk.word_tokenize(sent) for sent in sentences]
sentences = [nltk.pos_tag(sent) for sent in sentences]
print (sentences)