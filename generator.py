import nltk
from nltk.tag import pos_tag
from nltk.corpus import stopwords
from enum import Enum

import time

class IntoxicationLevel(Enum):
    TIPSY = 2
    DANCER = 3
    EVERYBODY_GETS_A_DRINK = 4
    FRIENDLY = 5
    FIGHTER = 6
    SLEEPY = 7
    HUNGRY = 8
    NEVER_DRINKING_AGAIN = 9
    TOO_MUCH = 12

    def next_level(self):
        if self is IntoxicationLevel.TIPSY:
            return IntoxicationLevel.DANCER
        elif self is IntoxicationLevel.DANCER:
            return IntoxicationLevel.EVERYBODY_GETS_A_DRINK
        elif self is IntoxicationLevel.EVERYBODY_GETS_A_DRINK:
            return IntoxicationLevel.FRIENDLY
        elif self is IntoxicationLevel.FRIENDLY:
            return IntoxicationLevel.FIGHTER
        elif self is IntoxicationLevel.FIGHTER:
            return IntoxicationLevel.SLEEPY
        elif self is IntoxicationLevel.SLEEPY:
            return IntoxicationLevel.HUNGRY
        elif self is IntoxicationLevel.HUNGRY:
            return IntoxicationLevel.NEVER_DRINKING_AGAIN
        else:
            return IntoxicationLevel.TOO_MUCH

class WordFinder(object):

    def __init__(self):
        # Construct a set of english stopwords that will be removed before
        # finding word frequencies
        self.stopwords = set(stopwords.words('english')) 

    def to_text(self, subtitles):
        return "\n".join([subtitle.content for subtitle in subtitles])

    def get_words(self, subtitles, minimum_frequency, maximum_frequency):
        text = self.to_text(subtitles)

        # Get words list from full subtitles text 
        words = nltk.word_tokenize(text)

        # Perform POS tagging of our words, get only NOUNS
        tags = pos_tag(words)
        nouns = set([word for word, tag in tags if tag.startswith('NN')])

        # Remove all words shorter than 1 character and all numbers
        words = [word for word in words if len(word) > 1]
        words = [word for word in words if not word.isnumeric()]

        # Lowercase all words and remove stopwords
        words = [word.lower() for word in words]
        words = [word for word in words if word not in self.stopwords]

        frequency_distribution = nltk.FreqDist(words)
        frequency_distribution = frequency_distribution.most_common(None)

        possible_words = []
        for word, frequency in frequency_distribution:
            # Skip words that don't appear enough times or are not nouns
            if frequency >= maximum_frequency or frequency < minimum_frequency:
                continue
            if word not in nouns:
                continue
            
            possible_words.append((word, frequency))
        return possible_words