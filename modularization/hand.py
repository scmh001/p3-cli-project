from config import VALUES

class Hand:
    def __init__(self):
        self.cards = []
        
    def add_card(self, card):
        self.cards.append(card)
        
    def calculate_value(self):
        value = sum(VALUES[card["rank"]] for card in self.cards)
        aces = sum(card["rank"] == "Ace" for card in self.cards)
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value