import random
import sqlite3
import argparse
import npyscreen

# Constants
SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11
}

# Database connection
DB_NAME = 'jack.db'


<<<<<<< HEAD
    
    def create(self):
        self.add(npyscreen.TitleText, name="Player Name:", rely=1, relx=2)
        self.add(npyscreen.ButtonPress, name="Hit", when_pressed_function=self.hit, rely=5, relx=2)
        self.add(npyscreen.ButtonPress, name="Stand", when_pressed_function=self.stand, rely=7, relx=2)
                # Player hand display
        self.player_hand_display = self.add(
            npyscreen.MultiLine,
            value=["Your hand will appear here"],
            editable=False,
            max_height=10,
            rely=9,
            relx=2,
            max_width=40
        )
        
        # Dealer hand display - adjusted 'relx' for better spacing
        self.dealer_hand_display = self.add(
            npyscreen.MultiLine,
            value=["Dealer's hand will appear here"],
            editable=True,
            max_height=10,
            rely=9,
            relx=45,  # Increased to provide clear separation
            max_width=40
        )
    # Initialize player_hand as an empty list
        self.player_hand = []
        self.dealer_hand = []  # Initialize dealer_hand as an empty list
=======
class BlackjackForm(npyscreen.ActionForm):
    def create(self):
        self.player_name_field = self.add(npyscreen.TitleText, name="Player Name:")
        self.hit_button = self.add(npyscreen.ButtonPress, name="Hit", when_pressed_function=self.hit)
        self.add(npyscreen.ButtonPress, name="Stand", when_pressed_function=self.stand)
        self.player_hand_display = self.add(npyscreen.MultiLineEdit, editable=False)
        self.dealer_hand_display = self.add(npyscreen.MultiLineEdit, editable=False)
        self.deck = create_deck()
        shuffle_deck(self.deck)
        self.player_hand = [deal_card(self.deck), deal_card(self.deck)]
        self.dealer_hand = [deal_card(self.deck), deal_card(self.deck)]
        self.display_hand(self.player_hand_display, self.player_hand, "Player")
        self.display_hand(self.dealer_hand_display, self.dealer_hand, "Dealer")

    def on_cancel(self):
        self.parentApp.setNextForm(None)
>>>>>>> 443366b5aa17d7724743fbf082eb2cb30d5b9173

    def hit(self):
        self.hit_button.editable = True  # Re-enable Hit button
        self.hit_button.display()  # Refresh the Hit button
        self.player_hand.append(deal_card(self.deck))
        self.display_hand(self.player_hand_display, self.player_hand, "Player")
        if calculate_hand_value(self.player_hand) > 21:
            self.stand()

    def stand(self):
        while calculate_hand_value(self.dealer_hand) < 17:
            self.dealer_hand.append(deal_card(self.deck))
        self.display_hand(self.dealer_hand_display, self.dealer_hand, "Dealer")
        self.check_winner()

    def on_ok(self):
        player_name = self.player_name_field.value
        add_player_if_not_exists(player_name)
        self.player_id = get_player_id(player_name)

    def display_hand(self, display, hand, player):
        display.value = ""
        for card in hand:
            display.value += f"{card['rank']} of {card['suit']}\n"
        display.value += f"Value: {calculate_hand_value(hand)}\n"
        display.display()

    def check_winner(self):
        player_value = calculate_hand_value(self.player_hand)
        dealer_value = calculate_hand_value(self.dealer_hand)
        outcome = ""
        if dealer_value > 21 or player_value > dealer_value:
            outcome = "Win"
            npyscreen.notify_confirm("You Win!", title="Play Again?")
        elif dealer_value > player_value or player_value > 21:
            outcome = "Loss"
            npyscreen.notify_confirm("You lose!", title="Game Over")
        else:
            outcome = "Tie"
            npyscreen.notify_confirm("Tie!", title="Play Again?")
        record_game_session(self.player_id, self.dealer_hand, self.player_hand, outcome)
        self.parentApp.setNextForm(None)


def create_deck():
    """Creates a deck of 52 cards."""
    return [{'suit': suit, 'rank': rank} for suit in SUITS for rank in RANKS]


def shuffle_deck(deck):
    """Shuffles the deck in place."""
    random.shuffle(deck)


def deal_card(deck):
    """Deals a card from the deck."""
    return deck.pop()


def calculate_hand_value(hand):
    """Calculates the value of a hand."""
    value = sum(VALUES[card['rank']] for card in hand)
    aces = sum(card['rank'] == 'Ace' for card in hand)
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value


def add_player_if_not_exists(player_name):
    """Adds a player to the database if they don't already exist."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO players (name) VALUES (?)", (player_name,))
        conn.commit()


def get_player_id(player_name):
    """Retrieves a player's ID from the database."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT player_id FROM players WHERE name = ?", (player_name,))
        player_id = cursor.fetchone()[0]
    return player_id


def record_game_session(player_id, dealer_hand, player_hand, outcome):
    """Records the outcome of a game session."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO game_sessions (player_id, dealer_hand_value, player_hand_value, outcome) VALUES (?, ?, ?, ?)",
            (player_id, calculate_hand_value(dealer_hand), calculate_hand_value(player_hand), outcome)
        )
        conn.commit()


class BlackjackApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm("MAIN", BlackjackForm)


def main():
    BlackjackApp().run()


if __name__ == "__main__":
    main()