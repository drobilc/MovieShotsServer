import nltk
from nltk.tag import pos_tag
from nltk.corpus import stopwords

from exceptions import *
import math, random, statistics

class DrinkingGame(object):

    def __init__(self, movie, subtitles, number_of_players, intoxication_level, number_of_bonus_words=1):
        self.id = "test"
        self.movie = movie
        self.subtitles = subtitles

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
        selected_words = players_words + random.choices(players_words, k=self.number_of_players - len(players_words))
        return [[element] for element in selected_words]
    
    def choose_less_or_more(self, words):
        # Find words that appear in epsilon-proximity of our intoxication_level
        # proximity = 2 means that it will try to find all words that appear
        # between intoxication_level - e and intoxication_level + e times
        # (inclusive) Use one fifth of the intoxication_level, so that bigger
        # intoxication levels (like 50) receive more options to choose from
        proximity = math.ceil(self.intoxication_level / 5)

        # Find words that have the exact number of occurences and those that do not
        exact_occurrences = list(filter(lambda x: x[1] == self.intoxication_level, words))
        non_exact_occurrences = list(filter(lambda x: abs(x[1] - self.intoxication_level) <= proximity and x[1] != self.intoxication_level, words))

        # If there are not words at all to choose from, raise an exception
        if (len(non_exact_occurrences) + len(exact_occurrences)) < self.number_of_players:
            raise GameGenerationException("There are not enough words for all players.")

        # Choose at most number_of_players of exact occurences and then add a
        # random selection of words with non exact occurences
        selected_words = random.sample(exact_occurrences, min(len(exact_occurrences), self.number_of_players))
        selected_words.extend(random.sample(non_exact_occurrences, self.number_of_players - len(selected_words)))
        return [[element] for element in selected_words]
    
    def choose_bonus_words(self, words):
        # Rare words are words that appear at most two times. Everybody drinks
        # when this word appears.
        rare_words = list(filter(lambda x: x[1] <= 2, words))
        if len(rare_words) <= 0:
            return []
        
        return random.sample(rare_words, self.number_of_bonus_words)
    
    def get_solutions(self, numbers, goal, depth, exact=False):
        solutions = []

        epsilon = 2 if not exact else 0

        possible_states = [(0, [])]
        while len(possible_states) > 0:
            state = possible_states.pop(0)
            if abs(goal - state[0]) <= epsilon:
                solutions.append(state)
            if len(state[1]) > depth:
                continue

            for number in numbers:
                new_value = state[0] + number
                if state[0] - goal >= epsilon:
                    continue
                new_state = (new_value, state[1] + [number])
                possible_states.append(new_state)
            
        return solutions
    
    def multiple_words(self, words):
        # This function will try to build
        occurrences = set(map(lambda x: x[1], filter(lambda x: x[1] <= self.intoxication_level, words)))

        # Compute all possible ways to get to intoxication_level number of shots
        # using iterative deepening algorithm with maximum number of word of 3,
        # because drunk people can not remember more than 3 words
        solutions = self.get_solutions(occurrences, self.intoxication_level, 1, exact=True)

        # Sort the solutions based on their standard deviation, because we want
        # as even number as possible in our word occurrences.
        sorted_solutions = sorted(solutions, key=lambda solution: statistics.pstdev(solution[1]))
        if len(sorted_solutions) <= 0:
            raise GameGenerationException

        players_words = []
        for player in range(self.number_of_players):
            selected_solutions = sorted_solutions[0:5]
            solution = random.choices(selected_solutions, weights=range(len(selected_solutions), 0, -1), k=1)[0]
            selected_words = []
            for occurrences in solution[1]:
                possible_words = list(filter(lambda x: x[1] == occurrences, words))
                selected_words.append(random.choice(possible_words))
            players_words.append(selected_words)

        return players_words

    def generate(self, subtitles):
        # Create a new word finder that will be used to get words that appear n
        # times in subtitles
        finder = WordFinder()

        # Get the list of nouns and number of their occurrences in subtitle text
        common_words = finder.get_words(self.subtitles)

        # Try to use two different functions to choose words:
        #   * choose_less_or_more - will try to construct a game from words that
        #     occur similar number of times as the requested intoxication_level
        #   * multiple_words - will construct a game from multiple words, the
        #     number of occurrences of all those words should match
        #     intoxication_level
        #
        #   there is a third option available, repeat_words, which will simply
        #   repeat words and can be used instead of the choose_less_or_more
        #   function
        """try:
            self.words = self.choose_less_or_more(common_words)
        except Exception as e:
            # The words could not be selected, try different function
            self.words = self.multiple_words(common_words)"""
        self.words = self.choose_less_or_more(common_words)
        
        self.bonus_words = self.choose_bonus_words(common_words)
    
    def to_dict(self):
        selected_words = []
        for player in self.words:
            player_words = []
            for word, occurrences in player:
                player_words.append({"word": word, "occurrences": occurrences})
            selected_words.append(player_words)

        return {
            "id": self.id,
            "movie": self.movie.to_dict(),
            "words": selected_words,
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