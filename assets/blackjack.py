import random
import sqlite3
import argparse
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

from prompt_toolkit.shortcuts import button_dialog

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


def add_player_if_not_exists(player_name, money):
    """Adds a player to the database if they don't already exist."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO players (name, money_bag) VALUES (?, ?)", (player_name, money,))
                      
        conn.commit()
        
# def add_new_player_money_bag(money):
#     money = 100
#     """Adds a players money_bag to the database if player doesn't already exist."""
#     with sqlite3.connect (DB_NAME) as conn:
#         cursor = conn.cursor()
#         cursor.execute("INSERT OR IGNORE INTO players (money_bag) VALUES (?)", (money))
#         conn.commit()


def get_player_id(player_name):
    """Retrieves a player's ID from the database."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT player_id FROM players WHERE name = ?", (player_name,))
        result = cursor.fetchone()
        if result is None:
            return None
        else:
            player_id = result[0]
            return player_id


def get_player_money_bag(player_id):
    """Retrieves a player's Money from the database"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT money_bag FROM players WHERE player_id = ?", (player_id,))
        result = cursor.fetchone()
        if result is None:
            return None
        else:
            money_bag = result[0]
            return money_bag
        
        
def update_player_money_bag(player_id, new_total):
    """Updates the players money_bag"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor=conn.cursor()
        sql_update_query = """
        UPDATE players
        SET money_bag = ?
        WHERE player_id = ?
        """
        cursor.execute(sql_update_query, (new_total, player_id))
        conn.commit()
    
#***************************************************************************************8
#
#Should record_game_session be recorded upon prompt from user after they're done playing?
#USER INPUT?
#
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
    print(header)
    print(instructions)
    while True:
        player_name = prompt("Please enter your player name: ").strip()
        while not player_name:
            console.print("Player name cannot be empty. Please enter a valid name.", style="bold red")
            player_name = prompt("Please enter your player name: ").strip()
       
        player_id = get_player_id(player_name)
        
        if player_id:
            money_bag = get_player_money_bag(player_id)
            if money_bag > 0:
                print(f'Welcome back to the game {player_name}, we have your ${money_bag} at the table for you')
            else:
                update_player_money_bag(player_id, 100)
                print(f'Welcome back to the game {player_name}. Looks like you had a bad run of cards\nlast round, we\'ve extended your credit another $100')
                money_bag = get_player_money_bag(player_id)
                print(f"Total Money: {money_bag}")
            

        else:
            initial_money = 100
            add_player_if_not_exists(player_name, initial_money)
            player_id = get_player_id(player_name)
            money_bag = initial_money
            print(f'Looks like we, haven\'t seen you before, we\'ll start you out with the max buy in of $100.')
            
        if  1 <= money_bag <= 300:
            print("Max table bet is $20:")
            bet_input = prompt("Please place your bet a number value less than or equal to $20:").strip()
            bet = int(bet_input)
            #########NEED TO FILTER INCORRECT BETS  ALL OF THIS COULD BE A HELPER METHOD
            new_bag = get_player_money_bag(player_id) - bet
            update_player_money_bag(player_id, new_bag)
            
        elif 301 <= money_bag <= 750:
            print("Max table bet is $50:")
            bet_input = prompt("Please place your bet a number value less than or equal to $50:").strip()
            bet = int(bet_input)
            new_bag = get_player_money_bag(player_id) - bet
            update_player_money_bag(player_id, new_bag)
            
        elif 751 <= money_bag <= 1000:
            print("Max table bet is $100:")
            bet_input = prompt("Please place your bet a number value less than or equal to $100:").strip()
            bet = int(bet_input)
            new_bag = get_player_money_bag(player_id) - bet
            update_player_money_bag(player_id, new_bag)
            
        elif 1001 <= money_bag <= 10000:
            print("Max table bet is $500:")
            bet_input = prompt("Please place your bet a number value less than or equal to $500:").strip()
            bet = int(bet_input)
            new_bag = get_player_money_bag(player_id) - bet
            update_player_money_bag(player_id, new_bag)
            
               
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
            print(f"Player busts! You lose ${bet} Dealer wins.")
            print(f"Total money: ${get_player_money_bag(player_id)}")
            outcome = "Loss"
            
        else:
            while calculate_hand_value(dealer_hand) < 17:
                dealer_hand.append(deal_card(deck))
            display_hand(dealer_hand, "Dealer")

            dealer_value = calculate_hand_value(dealer_hand)

            if dealer_value > 21:
                print(f"Dealer busts! Player wins ${bet}.")
                new_bag  = get_player_money_bag(player_id) + (2 * bet)
                update_player_money_bag(player_id, new_bag)
                print(f"Total money: ${get_player_money_bag(player_id)}")
                outcome = "Win"
                
            elif player_value > dealer_value:
                print(f"Player wins ${bet}!")
                new_bag  = get_player_money_bag(player_id) + (2 * bet)
                update_player_money_bag(player_id, new_bag)
                print(f"Total money: ${get_player_money_bag(player_id)}")
                outcome = "Win"
            elif player_value < dealer_value:
                print(f"Dealer wins! You lose ${bet}")
                print(f"Total money: ${get_player_money_bag(player_id)}")
                outcome = "Loss"
            else:
                print("It's a tie!")
                print(f"Total money: ${get_player_money_bag(player_id)}")
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