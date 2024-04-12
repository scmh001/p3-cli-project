import random
import sqlite3
import argparse
from rich.console import Console 
from rich.table import Table
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import yes_no_dialog
import npyscreen
from rich import box


# Constants
SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11
}

# Database connection
DB_NAME = 'jack.db'

class BlackjackForm(npyscreen.ActionForm):
    def __init__(self, *args, **kwargs):
        self.deck = kwargs.pop('deck', None)
        super().__init__(*args, **kwargs)

    def create(self):
        # Add widgets for player name input, hit button, stand button, and multi-line displays
        self.add(npyscreen.TitleText, name="Player Name:", rely=1, relx=2)
        self.add(npyscreen.ButtonPress, name="Hit", when_pressed_function=self.hit, rely=5, relx=2)
        self.add(npyscreen.ButtonPress, name="Stand", when_pressed_function=self.stand, rely=7, relx=2)
        self.player_hand_display = self.add(npyscreen.MultiLine, editable=False, max_height=10, rely=9, relx=2)
        self.dealer_hand_display = self.add(npyscreen.MultiLine, editable=False, max_height=10, rely=9, relx=30)
        # Initialize player_hand as an empty list
        self.player_hand = []
        self.dealer_hand = []  # Initialize dealer_hand as an empty list

    def hit(self):
        # Add a card to the player's hand
        self.player_hand.append(deal_card(self.deck))
        # Display the updated player's hand
        display_hand(self.player_hand, "Player")
        # Check if the player has busted
        if calculate_hand_value(self.player_hand) > 21:
            # Player busts, dealer wins
            outcome = "Loss"
            record_game_session(self.player_id, self.dealer_hand, self.player_hand, outcome)
            npyscreen.notify_confirm("Player busts! Dealer wins.", title="Game Over", wrap=True)
            self.parentApp.switchForm(None)  # Close the form and return to the main menu

    def stand(self):
        # Dealer reveals their second card
        display_hand(self.dealer_hand, "Dealer")
        # Dealer hits until their hand value is 17 or more
        while calculate_hand_value(self.dealer_hand) < 17:
            self.dealer_hand.append(deal_card(self.deck))
            display_hand(self.dealer_hand, "Dealer")
        # Determine the outcome of the game
        player_value = calculate_hand_value(self.player_hand)
        dealer_value = calculate_hand_value(self.dealer_hand)
        if dealer_value > 21 or player_value > dealer_value:
            outcome = "Win"
            npyscreen.notify_confirm("Player wins!", title="Game Over", wrap=True)
        elif dealer_value > player_value:
            outcome = "Loss"
            npyscreen.notify_confirm("Dealer wins!", title="Game Over", wrap=True)
        else:
            outcome = "Tie"
            npyscreen.notify_confirm("It's a tie!", title="Game Over", wrap=True)
        # Record the game session outcome
        record_game_session(self.player_id, self.dealer_hand, self.player_hand, outcome)
        self.parentApp.switchForm(None)  # Close the form and return to the main menu
        
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


def display_hand(hand, player):
    """Displays a player's hand using rich.Table."""
    console = Console()
    table = Table(show_header=False, box=box.HORIZONTALS)
    table.add_column("Rank", justify="center", style="dim", width=8)
    table.add_column("Suit", justify="center", style="dim", width=8)
    
    for card in hand:
        table.add_row(card['rank'], card['suit'])
    
    console.print(table)
    console.print(f"Value: {calculate_hand_value(hand)}\n")

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


def blackjack_game():
    """Main function to play a game of blackjack."""
    player_name = npyscreen.prompt("Please enter your player name: ").strip()
    while not player_name:
        npyscreen.notify_confirm("Player name cannot be empty. Please enter a valid name.", style="bold red")
        player_name = npyscreen.prompt("Please enter your player name: ").strip()

    add_player_if_not_exists(player_name)
    player_id = get_player_id(player_name)

    deck = create_deck()
    shuffle_deck(deck)

    player_hand = [deal_card(deck), deal_card(deck)]
    dealer_hand = [deal_card(deck), deal_card(deck)]

    display_hand(player_hand, "Player")
    display_hand(dealer_hand, "Dealer")

    while calculate_hand_value(player_hand) < 21:
        action = input("Do you want to hit or stand? ").lower()
        if action == "hit":
            player_hand.append(deal_card(deck))
            display_hand(player_hand, "Player")
        elif action == "stand":
            break

    player_value = calculate_hand_value(player_hand)
    dealer_value = calculate_hand_value(dealer_hand)

    if player_value > 21:
        print("Player busts! Dealer wins.")
        outcome = "Loss"
    else:
        while calculate_hand_value(dealer_hand) < 17:
            dealer_hand.append(deal_card(deck))
        display_hand(dealer_hand, "Dealer")

        dealer_value = calculate_hand_value(dealer_hand)

        if dealer_value > 21:
            print("Dealer busts! Player wins.")
            outcome = "Win"
        elif player_value > dealer_value:
            print("Player wins!")
            outcome = "Win"
        elif player_value < dealer_value:
            print("Dealer wins!")
            outcome = "Loss"
        else:
            print("It's a tie!")
            outcome = "Tie"

    record_game_session(player_id, dealer_hand, player_hand, outcome)


def view_game_outcomes():
    """Displays the outcomes of all game sessions using rich.Table."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        query = """
        SELECT game_sessions.player_id, players.name, game_sessions.dealer_hand_value,
               game_sessions.player_hand_value, game_sessions.outcome
        FROM game_sessions
        JOIN players ON game_sessions.player_id = players.player_id
        """
        try:
            cursor.execute(query)
            outcomes = cursor.fetchall()

            console = Console()
            table = Table(show_header=True, header_style="bold blue")
            table.add_column("Player ID", style="dim", width=12)
            table.add_column("Player Name", style="dim", width=20)
            table.add_column("Dealer Hand Value", justify="right", style="dim", width=20)
            table.add_column("Player Hand Value", justify="right", style="dim", width=20)
            table.add_column("Outcome", justify="right", style="dim", width=15)

            for outcome in outcomes:
                player_id, player_name, dealer_hand_value, player_hand_value, game_outcome = outcome
                table.add_row(str(player_id), player_name, str(dealer_hand_value), str(player_hand_value), game_outcome)

            console.print(table)

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")

def main():
    """Main function to handle command-line arguments and start the game."""
    parser = argparse.ArgumentParser(description="CLI Blackjack Game")
    parser.add_argument('--play', action='store_true', help='Start a new game of blackjack')
    parser.add_argument('--view', action='store_true', help='View game outcomes')
    args = parser.parse_args()

    if args.play:
        blackjack_game()
    elif args.view:
        view_game_outcomes()
    else:
        parser.print_help()


def run_game(stdscr):
    """Function to run the game within curses."""
    deck = create_deck()  # Create the deck
    shuffle_deck(deck)  # Shuffle the deck

    class PlayerNameForm(npyscreen.Form):
        def create(self):
            self.player_name = self.add(npyscreen.TitleText, name="Player Name:")

    player_name_form = PlayerNameForm(name="Player Name")
    player_name_form.edit()
    player_name = player_name_form.player_name.value.strip()

    while not player_name:
        npyscreen.notify_confirm("Player name cannot be empty. Please enter a valid name.", style="bold red")
        player_name_form.edit()
        player_name = player_name_form.player_name.value.strip()

    add_player_if_not_exists(player_name)
    player_id = get_player_id(player_name)

    form = BlackjackForm(name="Blackjack Game", deck=deck, player_id=player_id)  # Pass the player_id as an argument
    form.player_id = player_id  # Set the player_id attribute
    form.edit()


if __name__ == "__main__":
    npyscreen.wrapper_basic(run_game)