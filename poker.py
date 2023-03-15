import time
import os
from enum import Enum
import random
# Important for unique object ids
import itertools
import pygame

# General Poker Simulation Library:
# This small library allows for the analysis of poker games and stratagies
# using a universal interface and class structure. It can be used to test
# strategies, run through probabilities, and much more

# Enumerations for card suit and rank
class Suit(Enum):
	HEARTS = 1
	DIAMONDS = 2
	CLUBS = 3
	SPADES = 4

class Rank(Enum):
	ACE = 1
	TWO = 2
	THREE = 3
	FOUR = 4
	FIVE = 5
	SIX = 6
	SEVEN = 7
	EIGHT = 8
	NINE = 9
	TEN = 10
	JACK = 11
	QUEEN = 12
	KING = 13

class Hand(Enum):
	HIGH_CARD = 1
	ONE_PAIR = 2
	TWO_PAIR = 3
	THREE_OF_A_KIND = 4
	STRAIGHT = 5
	FLUSH = 6
	FULL_HOUSE = 7
	FOUR_OF_A_KIND = 8
	STRAIGHT_FLUSH = 9
	ROYAL_STRAIGHT_FLUSH = 10

class Strategy(Enum):
	DONOTHING = 1
	SIM = 2
	SCARED = 3


class Card:
	def __init__(self, suit, rank):
		self.suit = suit
		self.rank = rank
	def __str__(self):
		return f"{self.rank}({self.suit})"

# Class representing a deck of cards
# Can be shuffled or left orderly 
class Deck:
	def __init__(self, isShuffled):
		self.card_deck = []
		# Grab enums for both rank and suit
		ranks = list(Rank)
		suits = list(Suit)
		# Generate full deck of 52 cards
		for i in range(4):
			for j in range(13):
				self.card_deck.append(Card(suits[i], ranks[j]))

		# If the deck is to be shuffled
		if isShuffled:
			random.shuffle(self.card_deck)

	def shuffle(self):
		random.shuffle(self.card_deck)

	def getCount(self):
		return len(self.card_deck)

	def dealCards(self, numberOfCards):
		ret = []
		for i in range(numberOfCards):
			ret.append(self.card_deck.pop())
		return ret

	def getCard(self, value, suit):
		#return [n for n in self.card_deck if n.suit == suit and n.rank == rank]
		return [n for n in self.card_deck]

	def burnCard(self):
		self.card_deck.pop()


# Player class
# Holds player's hand
class Player:
	# Iterative counter for unqiue object ids
	# This is necessary to simplify object data integrity
	id_iter = itertools.count()

	def __init__(self, bankroll, strategy):
		self.id = next(self.id_iter)
		self.hand = []
		self.bankroll = bankroll
		self.strategy = strategy

	def setHand(self, hand):
		self.hand = hand

	def getHand(self):
		return self.hand

	# Sets bet, returns False if bankroll <= 0
	def setBet(self, bet):
		self.bankroll -= bet
		return self.bankroll <= 0

	# Evaluates player's hand when comparing
	def evalHand(self, community_cards):
		# Combine all cards into one pile
		all_cards = community_cards + self.hand

		t_suits = [t_card.suit.value for t_card in all_cards]
		t_ranks = [t_card.rank.value for t_card in all_cards]

		#print("Initial Cards")
		#print(t_suits)
		#print(t_ranks)

		# Temporarily change all Aces to '14' instead of '1' for pairs
		t_ranks = [14 if x == 1 else x for x in t_ranks]
		#list(map(lambda x: 14 if x == 1 else x, rank_types))

		rank_types = []
		# Create histogram of each rank
		for x in t_ranks:
			if x not in rank_types:
				rank_types.append(x)

		frequency = [t_ranks.count(x) for x in rank_types]

		#print(rank_types)
		#print(frequency)

		ret = []
		index = 0
		matches = []

		# Check for high-card
		ret = [Hand.HIGH_CARD, max(t_ranks)]

		# Check for largest frequency
		if 4 in frequency:
			ret = [Hand.FOUR_OF_A_KIND, rank_types[frequency.index(4)]]
		elif 3 in frequency:
			if 2 in frequency:
				# Check for multiple pairs and find the best
				matches = [i for i, n in enumerate(frequency) if n == 2]
				max_rank = max([rank_types[n] for n in matches])
				ret = [Hand.FULL_HOUSE, rank_types[frequency.index(3)], max_rank]
			else:
				# Check for multiple pairs and find the best
				matches = [i for i, n in enumerate(frequency) if n == 3]
				max_rank = max([rank_types[n] for n in matches])
				ret = [Hand.THREE_OF_A_KIND, max_rank]
		elif 2 in frequency:
			# If only one pair is found
			if frequency.count(2) == 1:
				ret = [Hand.ONE_PAIR, rank_types[frequency.index(2)]]
			else:
				# Check for multiple pairs and find the best 2 out of n
				# This should work regardless of the number of possible pairs that can be made
				matches = [i for i, n in enumerate(frequency) if n == 2]
				temp = [rank_types[n] for n in matches]
				#print(temp)
				max_rank_1 = max(temp)
				temp.pop(temp.index(max_rank_1))
				max_rank_2 = max(temp)
				ret = [Hand.TWO_PAIR, max_rank_1, max_rank_2]

		# Check for Straights
		# Sort ranks in reverse, then compare difference between each value
		sorted_ranks = t_ranks.copy()
		sorted_ranks.sort(reverse=True)
		ranks_diff = [sorted_ranks[i] - sorted_ranks[i + 1] for i in range(len(sorted_ranks) - 1)]

		#print(sorted_ranks)
		#print(ranks_diff)

		# Run through array to check for consistent
		index = -1
		count = 0
		for i in range(len(ranks_diff)):
			if ranks_diff[i] == 1:
				if count == 0:
					index = i
				count += 1
			else:
				count = 0
				index = -1
			if count == 4:
				break

		# Check for low-value ace straight
		if count == 3 and 14 in t_ranks and ret[0] != Hand.FOUR_OF_A_KIND:
			ret = [Hand.STRAIGHT, 5]

		# Check for any straight
		if count == 4:
			ret = [Hand.STRAIGHT, sorted_ranks[index]]

		# Check for Straight flushes:
		# NEED TO DO

		# Check for Flushes
		# First calculate a histogram of suits, then check for a total of 5 on any suit
		suit_types = [1,2,3,4]
		frequency = [t_suits.count(x) for x in suit_types]

		#print(t_suits)
		#print(frequency)

		flush_cards = []
		if 5 in frequency and ret[0] != Hand.STRAIGHT_FLUSH:
			# Check for maximum number in suit
			max_suit = frequency.index(5) + 1
			for i in range(len(t_ranks)):
				#print(str(t_suits[i]) + " " + str(t_ranks[i]))
				if t_suits[i] == max_suit:
					flush_cards.append(t_ranks[i])

			flush_cards.sort(reverse=True)
			ret = [Hand.FLUSH] + flush_cards


		return ret

	# Decides what a player's current move will be given:
	# 1) The current bet (can be 0 for no bet)
	# 2) Whether it is Big, little, or no blind
	# 3) What the current community cards are
	# 4) List of all players
	def getMove(self, current_bet, blind, community_cards, players):
		pass



# Very basic Game function, used to statistics
def Game():
	#while True:
		#print("Input up to 2 cards for your hand:   Ex. [3s, 4h] (using t, j, q, k, and a; and for suits use h, d, s, c)"
		#player_input = input(">")

		#print("Input up to 4 community cards:   Ex. [3s, 4h] (using t, j, q, k, and a; and for suits use h, d, s, c)"
		#player_input = input(">")

		#print("Input number of games to test with:"
		#total_games = input(">")

		# Variables for Stats
		p1_win = 0 # Number of times Player 1 has won
		p2_win = 0 # Number of times Player 2 has won
		ties = 0 # Number of ties

		hand_stats = [0,0,0,0,0,0,0,0,0,0] # Keeps track of how many total hands of each type have won

		total_games = 10000

		for i in range(total_games):
			d = Deck(True)
			p1 = Player(250, 0)
			p2 = Player(250, 0)

			# Simple Texas Holdem game:
			p1.setHand(d.dealCards(2))
			p2.setHand(d.dealCards(2))

			# Burn card and draw the flop
			d.burnCard()
			community_cards = d.dealCards(3)

			# Burn and and draw the turn
			d.burnCard()
			community_cards = community_cards + d.dealCards(1)

			# Burn and and draw the river
			d.burnCard()
			community_cards = community_cards + d.dealCards(1)

			# Get Player hands
			res1 = p1.evalHand(community_cards)
			res2 = p2.evalHand(community_cards)

			hand_stats[res1[0].value - 1] += 1
			hand_stats[res2[0].value - 1] += 1

			if res1[0].value > res2[0].value:
				p1_win += 1
			elif res2[0].value > res1[0].value:
				p2_win += 1
			else:
				ret = breakTie(res1, res2)
				if ret == 1:
					p1_win += 1
				elif ret == 2:
					p2_win += 1
				else:
					ties += 1
			# print(res1)
			# print(res2)
			# Update screen for every 100 games played
			if(i % 100 == 0):
				os.system('clear')
				print("Total Number of Games: " + str(i))

				temp_stats = [x/(i*2+1) for x in hand_stats]
				for n in range(9):
					print(["High Card", "One Pair", "Two Pair", "Three of a kind", "Straight", "Flush", "Full House", "Four of a kind", "Straight Flush"][n] + ": " + str(temp_stats[n]))


# A function designed to break/decide ties (if possible)
def breakTie(res1, res2):

	# Decide whether ties are actually ties in order from least to most significant
	if res1[0] == Hand.HIGH_CARD or res1[0] == Hand.ONE_PAIR or res1[0] == Hand.THREE_OF_A_KIND or res1[0] == Hand.FOUR_OF_A_KIND or res1[0] == Hand.STRAIGHT:
		if res1[1] > res2[1]:
			return 1
		elif res2[1] > res1[1]:
			return 2
		else:
			return 3
	if res1[0] == Hand.TWO_PAIR or res1[0] == Hand.FULL_HOUSE:
		if res1[1] > res2[1]:
			return 1
		elif res2[1] > res1[1]:
			return 2
		else:
			if res1[2] > res2[2]:
				return 1
			elif res2[2] > res1[2]:
				return 2
			else:
				return 3

	if res1[0] == Hand.FLUSH:
		for i in range(len(res1) - 1):
			if res1[i+1] > res2[i+1]:
				return 1
			if res2[i+1] > res1[i+1]:
				return 2
		return 3
	return 3



# Card Creation for testing
def createCard(rank, suit):
	return Card(list(Suit)["hdcs".index(suit)], list(Rank)["a23456789tjqk".index(rank)])


if __name__ == '__main__':
	Game()
