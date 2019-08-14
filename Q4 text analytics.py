import pandas as pd
from textblob import TextBlob
from textblob.np_extractors import FastNPExtractor
import sqlite3

df = pd.read_csv('tareview.csv')
pd.set_option('display.max_colwidth', -1)

#iterates through reviews to find keywords
food_words=['food', 'breakfast','lunch','dinner','cuisine']
restaurant_words = ['restaurant']
room_words = ['room','suite','view','bed']
service_words = ['service','chef','waiter','bellboy','receptionist','staff']
price_words = ['price','cost']
general_words = ['general','location','experience']
keywords = [food_words, restaurant_words, room_words, service_words, price_words, general_words]

def classify_category(row):
    lower_single_words = TextBlob(str(row['review'])).pos_tags
    #tags for nouns(for categorisation)
    noun_tags = ['NN','NNS']
    nouns = [word[0].lower() for word in lower_single_words if word[-1] in noun_tags]
    categories = []
    for word in nouns:
        category = check_category(str(word))
        if category:
            categories.append(category)
    if len(categories) == 0:
        categories.append('general')
    final_category = most_common(categories)
    return final_category

#function to find most common category
def most_common(categories):
    return max(set(categories), key=categories.count)
    
def check_category(word):
    for wordlist in keywords:
        if word in wordlist:
            return wordlist[0]


#sentiment level ranges as a float form from -1 to 1 
def check_sentiment(row):
    sentiment = TextBlob(str(row['review'])).sentiment.polarity
    return sentiment

#finds index of sentence of max. absolute polarity in list of sentences
def sort_by_polarity(sentences):
    sentence_polarity = [abs(sentence.sentiment.polarity) for sentence in sentences]
    highest_index = [i for i,j in enumerate(sentence_polarity) if j==max(sentence_polarity)]
    return highest_index[0]

#returns key phrases in sentence of highest polarity in review
def check_keyword(row):
    sentences = TextBlob(str(row['review'])).sentences
    if len(sentences)>1:
        #slice to get most polarised sentence
        sentences = sentences[sort_by_polarity(sentences)]       
    try:    
        keywords = sentences.noun_phrases
    except AttributeError:
        keywords = sentences[0].noun_phrases
    final_keywords = ''
    for keyword in keywords:
        final_keywords = final_keywords + keyword + ','
    return final_keywords

def check_entity(row):
    lower_single_words = TextBlob(str(row['review'])).pos_tags
    pronoun_tags = ['NNP','NNPS']
    entities = [word[0] for word in lower_single_words if word[-1] in pronoun_tags]
    final_entities = ''
    for entity in entities:
        final_entities = final_entities + entity + ','
    return final_entities


def main():
    df['category'] = df.apply(classify_category, axis = 1)
    df['sentiment'] = df.apply(check_sentiment, axis = 1)
    df['keywords'] = df.apply(check_keyword, axis = 1)
    df['entities'] = df.apply(check_entity, axis = 1)
    
    #write to database
    conn = sqlite3.connect('tareview.db')
    c = conn.cursor()
    df.to_sql(name='analysis', con=conn, if_exists='replace',index=False)
    conn.commit()
    conn.close()
    
if __name__ == '__main__':
    main()
