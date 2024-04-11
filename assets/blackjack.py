import random
import sqlite3
import argparse
import outcomes

# Constants
SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
VALUES = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
          'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11}

# Functions
def create_deck():
    return [{'suit': suit, 'rank': rank} for suit in SUITS for rank in RANKS]

def shuffle_deck(deck):
    random.shuffle(deck)
    return deck

def deal_card(deck):
    return deck.pop()

def calculate_value(hand):
    value = sum(VALUES[card['rank']] for card in hand)
    aces = sum(card['rank'] == 'Ace' for card in hand)
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

def display_hand(hand, player):
    print(f"{player}'s hand:")
    for card in hand:
        print(f"{card['rank']} of {card['suit']}")
    print("Value:", calculate_value(hand))
    print()

def blackjack_game():
    player_name = "Player 1"  # This could be dynamic based on user input
    add_player_if_not_exists(player_name)
    player_id = get_player_id(player_name)
    player_name = ""
    while not player_name.strip():
        player_name = input("Please enter your player name: ")
        if not player_name.strip():
            print("Player name cannot be empty. Please enter a valid name.")
    
    add_player_if_not_exists(player_name)
    player_id = get_player_id(player_name)
    
    deck = create_deck()
    shuffle_deck(deck)

    player_hand = [deal_card(deck), deal_card(deck)]
    dealer_hand = [deal_card(deck), deal_card(deck)]

    display_hand(player_hand, "Player")
    display_hand(dealer_hand, "Dealer")

    while calculate_value(player_hand) < 21:
        action = input("Do you want to hit or stand? ").lower()
        if action == "hit":
            player_hand.append(deal_card(deck))
            display_hand(player_hand, "Player")
        elif action == "stand":
            break

    if calculate_value(player_hand) > 21:
        print("Player busts! Dealer wins.")
        return

    while calculate_value(dealer_hand) < 17:
        dealer_hand.append(deal_card(deck))

    display_hand(dealer_hand, "Dealer")

    player_value = calculate_value(player_hand)
    dealer_value = calculate_value(dealer_hand)

    if dealer_value > 21:
        print("Dealer busts! Player wins.")
    elif player_value > dealer_value:
        print("Player wins!")
    elif player_value < dealer_value:
        print("Dealer wins!")
    else:
        print("It's a tie!")
        
    # Connect to the database
    conn = sqlite3.connect('jack.db')
    cursor = conn.cursor()


    # Play the game

    # Record the game session outcome
    outcome = "Win"  # This should be determined based on the game logic
    cursor.execute("INSERT INTO game_sessions (player_id, dealer_hand_value, player_hand_value, outcome) VALUES (?, ?, ?, ?)",
                   (player_id, calculate_value(dealer_hand), calculate_value(player_hand), outcome))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
def add_player_if_not_exists(player_name):
    conn = sqlite3.connect('jack.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO players (name) VALUES (?)", (player_name,))
    conn.commit()
    conn.close()

def get_player_id(player_name):
    conn = sqlite3.connect('jack.db')
    cursor = conn.cursor()
    cursor.execute("SELECT player_id FROM players WHERE name = ?", (player_name,))
    player_id = cursor.fetchone()[0]
    conn.close()
    return player_id
    
def main():
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

def view_game_outcomes():
    # Connect to the SQLite database
    conn = sqlite3.connect('jack.db')
    cursor = conn.cursor()
    
    # SQL query to select game outcomes
    query = "SELECT game_sessions.player_id, players.name, game_sessions.dealer_hand_value, game_sessions.player_hand_value, game_sessions.outcome FROM game_sessions JOIN players ON game_sessions.player_id = players.player_id"
    
    try:
        cursor.execute(query)
        outcomes = cursor.fetchall()
        
        # Check if there are any outcomes to display
        if outcomes:
            print("Game Outcomes:\n")
            print(f"{'Player ID':<10} {'Player Name':<20} {'Dealer Hand':<12} {'Player Hand':<12} {'Outcome':<10}")
            for outcome in outcomes:
                player_id, player_name, dealer_hand_value, player_hand_value, game_outcome = outcome
                print(f"{player_id:<10} {player_name:<20} {dealer_hand_value:<12} {player_hand_value:<12} {game_outcome:<10}")
        else:
            print("No game outcomes found.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the database connection
        conn.close()

if __name__ == "__main__":
    main()

# Main game loop
if __name__ == "__main__":
    while True:
        blackjack_game()
        play_again = input("Do you want to play again? (yes/no) ").lower()
        if play_again != "yes":
            break