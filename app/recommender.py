import nltk
import re

nltk.download('punkt')
nltk.download('maxent_treebank_pos_tagger')
nltk.download('averaged_perceptron_tagger')

from nltk import word_tokenize, pos_tag

class Recommender:
	"""docstring for Recommender"""
	def __init__(self, bio):
		self.bio = bio

	def tag_words(self):
		tokenized_text = word_tokenize(self.bio)
		tagged_words = pos_tag(tokenized_text)
		tagged_words_filtered = []
		# Filter out words that aren't nouns, verbs and adverbs
		pattern1 = re.compile("V.*")
		pattern2 = re.compile("N.*")
		pattern3 = re.compile("R.*")
		for (word, tag) in tagged_words:
			if pattern1.match(tag) or pattern2.match(tag) or pattern3.match(tag):
				tagged_words_filtered.append(word.lower())

		return tagged_words_filtered
