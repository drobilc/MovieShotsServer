import nltk
from enum import Enum

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
        pass

    def to_text(self, subtitles):
        return "\n".join([subtitle.content for subtitle in subtitles])

    def get_words(self, subtitles, minimum_frequency, maximum_frequency):
        text = self.to_text(subtitles)

        words = nltk.word_tokenize(text)
        words = [word for word in words if len(word) > 1]
        words = [word for word in words if not word.isnumeric()]
        words = [word.lower() for word in words]

        frequency_distribution = nltk.FreqDist(words)
        frequency_distribution = frequency_distribution.most_common(None)

        possible_words = []
        for word, frequency in frequency_distribution:
            if frequency >= maximum_frequency or frequency < minimum_frequency:
                continue
            possible_words.append((word, frequency))
        return possible_words