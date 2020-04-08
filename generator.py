import nltk
from nltk.tag import pos_tag
from nltk.corpus import stopwords

from exceptions import *
import random

class DrinkingGame(object):

    def __init__(self, movie, subtitles, number_of_players, intoxication_level, number_of_bonus_words=1):
        self.movie = movie
        self.subtitles = subtitles

        # This funnction will be called when choosing words. The
        # choose_less_or_more function can choose words that have approximately
        # the same number of shots. The repeat_words function simply repeats the
        # words with exact number of appearances.
        self.choosing_function = self.choose_less_or_more
        # self.choosing_function = self.repeat_words

        self.number_of_players = number_of_players
        self.intoxication_level = intoxication_level
        self.number_of_bonus_words = number_of_bonus_words
        self.words = []
        self.bonus_words = []

        # Generate game based on received subtitles
        self.generate(self.subtitles)
    
    def repeat_words(self, words):
        # Filter the list of words and only get words that appear EXACTLY
        # intoxication_level number of times
        players_words = list(filter(lambda x: x[1] == self.intoxication_level, words))

        # If there are not words at all to choose from, raise an exception
        if len(players_words) <= 0:
            raise GameGenerationException

        # If there are enough words, return a random selection of them,
        # otherwise randomly choose them and allow repeating
        if len(players_words) >= self.number_of_players:
            return random.sample(players_words, self.number_of_players)
        
        # We need to sample self.number_of_players - len(players_words) of words
        # from the same list
        return players_words + random.choices(players_words, k=self.number_of_players - len(players_words))
    
    def choose_less_or_more(self, words):
        # Find words that appear in epsilon-proximity of our intoxication_level
        # proximity = 2 means that it will try to find all words that appear
        # between intoxication_level - 2 and intoxication_level + 2 times
        # (inclusive)
        proximity = 2

        # Find words that have the exact number of occurences and those that do not
        exact_occurrences = list(filter(lambda x: x[1] == self.intoxication_level, words))
        non_exact_occurrences = list(filter(lambda x: abs(x[1] - self.intoxication_level) <= proximity and x[1] != self.intoxication_level, words))
        

        # If there are not words at all to choose from, raise an exception
        if (len(non_exact_occurrences) + len(exact_occurrences)) < self.number_of_players:
            raise GameGenerationException

        # Choose at most number_of_players of exact occurences and then add a
        # random selection of words with non exact occurences
        selected_words = random.sample(exact_occurrences, min(len(exact_occurrences), self.number_of_players))
        selected_words.extend(random.sample(non_exact_occurrences, self.number_of_players - len(selected_words)))
        return selected_words
    
    def choose_bonus_words(self, words):
        # Rare words are words that appear at most two times. Everybody drinks
        # when this word appears.
        rare_words = list(filter(lambda x: x[1] <= 2, words))
        if len(rare_words) <= 0:
            return []
        
        return random.sample(rare_words, self.number_of_bonus_words)

    def generate(self, subtitles):
        # Create a new word finder that will be used to get words that appear n
        # times in subtitles
        finder = WordFinder()

        # The bonus words are words where all players have to drink. Because
        # each player already has to drink self.intoxication_level number of
        # shots, we should only find words that appear one or two times.
        common_words = finder.get_words(self.subtitles)

        # We now have words that appear between 1 and intoxication_level of
        # times (inclusive) in subtitles. Some movies don't have enough words
        # for all players to chose from. Use choosing function to choose words.
        self.words = self.choosing_function(common_words)
        self.bonus_words = self.choose_bonus_words(common_words)
    
    def to_dict(self):
        return {
            # "movie": self.movie.to_dict(),
            "words": [{"word": word, "occurrences": occurrences} for word, occurrences in self.words],
            "bonus_words": [{"word": word, "occurrences": occurrences} for word, occurrences in self.bonus_words]
        }

class WordFinder(object):

    def __init__(self):
        # Construct a set of english stopwords that will be removed before
        # finding word frequencies
        self.stopwords = set(stopwords.words('english')) 

    def to_text(self, subtitles):
        return "\n".join([subtitle.content for subtitle in subtitles])

    def get_words(self, subtitles):
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
            # Skip words that are not nouns, because it is not interesting to
            # drink to them
            if word not in nouns:
                continue

            possible_words.append((word, frequency))
        return possible_words