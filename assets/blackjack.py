import random
import sqlite3
import argparse
import click
from rich.console import Console
from rich.table import Table
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import yes_no_dialog
from ascii import deck_of_cards
from instructions import header, instructions

# Constants
SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11
}

# Database connection
DB_NAME = 'jack.db'


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
    """Displays a player's hand with the name of each card above its ASCII art."""
    console = Console()
    console.print(f"{player}'s hand:")

    for card in hand:
        # Construct the card name
        card_name = f"{card['rank']} of {card['suit']}"
        
        # Retrieve the ASCII art for the card
        ascii_art = deck_of_cards.get(card_name, "Card not found")
        
        # Print the card name above its ASCII art
        console.print(card_name)
        console.print(ascii_art)
        
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
    while True:
    print(header)
    print(instructions)
    player_name = prompt("Please enter your player name: ").strip()
    while not player_name:
        console.print("Player name cannot be empty. Please enter a valid name.", style="bold red")
        player_name = prompt("Please enter your player name: ").strip()
        while not player_name:
            console.print("Player name cannot be empty. Please enter a valid name.", style="bold red")
            player_name = prompt("Please enter your player name: ").strip()

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
        
        play_again = input("Do you want to play again? (yes/no): ").lower()
        if play_again != "yes":
            print("Thanks for playing!")
            break


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


if __name__ == "__main__":
    main()