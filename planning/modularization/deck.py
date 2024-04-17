import random
from config import RANKS, SUITS, VALUES

class Deck:
    def __init__(self):
        self.cards = self.create_deck()
        
    def create_deck(self):
        return [{"suit": suit, "rank": rank} for suit in SUITS for rank in RANKS]
    
    def shuffle(self):
        random.shuffle(self.cards)
        
    def deal_card(self):
        return self.cards.pop()