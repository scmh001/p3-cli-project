import os
import random
# import openai
import os
# import pygame
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from prompt_toolkit import prompt
from ascii import deck_of_cards
from instructions import header, instructions
from config import SUITS, RANKS, VALUES
from database import get_db_engine, init_db, Player, GameSession
from sqlalchemy.orm import sessionmaker
from api_key import api_key

console = Console()

openai.api_key= api_key

# def get_play_suggestion(state: dict) -> str:
#     """Get play suggestion from GPT-3."""
#     prompt_text = f"Given the current game state:\nPlayer hand: {state['player_hand']}\nDealer hand: {state['dealer_hand']}\nShould I hit or stand?"
#     response = openai.Completion.create(
#         model="davinci-002",
#         prompt=prompt_text,
#         temperature=0.1,
#         max_tokens=50
#     )
#     suggestion = response.choices[0].text.strip()
#     return suggestion



    
def create_deck() -> List[Dict[str, str]]:
    """Creates a deck of 52 cards."""
    return [{'suit': suit, 'rank': rank} for suit in SUITS for rank in RANKS]

def shuffle_deck(deck: List[Dict[str, str]]) -> None:
    """Shuffles the deck in place."""
    random.shuffle(deck)
    

def deal_card(deck: List[Dict[str, str]]) -> Dict[str, str]:
    """Deals a card from the deck."""
    return deck.pop()

def calculate_hand_value(hand: List[Dict[str, str]]) -> int:
    """Calculates the value of a hand."""
    value = sum(VALUES[card['rank']] for card in hand)
    aces = sum(card['rank'] == 'Ace' for card in hand)
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

def display_hand(hand: List[Dict[str, str]], player: str) -> None:
    """Displays a player's hand with the name of each card above its ASCII art."""
    console.print(f"{player}'s hand:")

    for card in hand:
        card_name = f"{card['rank']} of {card['suit']}"
        ascii_art = deck_of_cards.get(card_name, "Card not found")
        console.print(card_name)
        console.print(ascii_art)
        
    console.print(f"Value: {calculate_hand_value(hand)}\n")

def get_or_create_player(session, name):
    """Gets or creates a player by name."""
    player = session.query(Player).filter_by(name=name).first()
    if not player:
        player = Player(name=name)
        session.add(player)
        session.commit()
    return player

def record_game_session(session, player_id, dealer_hand, player_hand, outcome):
    """Records the outcome of a game session."""
    game_session = GameSession(
        player_id=player_id,
        dealer_hand_value=calculate_hand_value(dealer_hand),
        player_hand_value=calculate_hand_value(player_hand),
        outcome=outcome
    )
    session.add(game_session)
    session.commit()

def get_user_input(prompt_text: str) -> str:
    """Gets user input and validates it."""
    while True:
        user_input = prompt(prompt_text).strip().lower()
        if user_input:
            return user_input
        else:
            console.print("Invalid input. Please try again.", style="bold red")

def display_game_outcome(player_hand_value: int, dealer_hand_value: int) -> str:
    """Displays the outcome of the game and returns it as a string."""
    if player_hand_value > 21:
        console.print("Player busts! Dealer wins.")
        return "Loss"
    elif dealer_hand_value > 21:
        console.print("Dealer busts! Player wins.")
        return "Win"
    elif player_hand_value > dealer_hand_value:
        console.print("Player wins!")
        return "Win"
    elif player_hand_value < dealer_hand_value:
        console.print("Dealer wins!")
        return "Loss"
    else:
        console.print("It's a tie!")
        return "Tie"

def play_game(session) -> None:
    """Handles the game logic for a single game of blackjack."""
    os.system("clear")
    deck = create_deck()
    shuffle_deck(deck)

    player_hand = [deal_card(deck), deal_card(deck)]
    dealer_hand = [deal_card(deck), deal_card(deck)]

    display_hand(player_hand, "Player")
    display_hand(dealer_hand, "Dealer")

    while calculate_hand_value(player_hand) < 21:
        action = get_user_input("Do you want to hit, stand or get help? ")
        if action == "hit":
            os.system("clear")
            player_hand.append(deal_card(deck))
            display_hand(player_hand, "Player")
            display_hand(dealer_hand, "Dealer")
        elif action == "stand":
            break
        elif action == "help":
            suggestion = get_play_suggestion({"player_hand": player_hand, "dealer_hand": dealer_hand})
            console.print("Suggested play:", style="bold green")
            console.print(suggestion)
            continue

    player_hand_value = calculate_hand_value(player_hand)

    while calculate_hand_value(dealer_hand) < 17:
        dealer_hand.append(deal_card(deck))
    display_hand(dealer_hand, "Dealer")

    dealer_hand_value = calculate_hand_value(dealer_hand)

    outcome = display_game_outcome(player_hand_value, dealer_hand_value)
    return dealer_hand, player_hand, outcome

def blackjack_game(session) -> None:
    """Main function to play a game of blackjack."""
    console.print(header)
    console.print(instructions)
    while True:
        player_name = get_user_input("Please enter your player name: ")
        player = get_or_create_player(session, player_name)
        
        dealer_hand, player_hand, outcome = play_game(session)
        record_game_session(session, player.id, dealer_hand, player_hand, outcome)
        
        play_again = get_user_input("Do you want to play again? (yes/no): ")
        if play_again != "yes":
            console.print("Thanks for playing!")
            break

def view_game_outcomes(session) -> None:
    """Displays the outcomes of all game sessions using rich.Table."""
    query = session.query(
        GameSession.player_id, 
        Player.name,
        GameSession.dealer_hand_value,
        GameSession.player_hand_value,
        GameSession.outcome
    ).join(Player)
    
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Player ID", style="dim", width=12)
    table.add_column("Player Name", style="dim", width=20)
    table.add_column("Dealer Hand Value", justify="right", style="dim", width=20) 
    table.add_column("Player Hand Value", justify="right", style="dim", width=20)
    table.add_column("Outcome", justify="right", style="dim", width=15)

    for game_session in query:
        table.add_row(
            str(game_session.player_id),
            game_session.name, 
            str(game_session.dealer_hand_value),
            str(game_session.player_hand_value),
            game_session.outcome
        )
        
    console.print(table)

def main() -> None:
    """Main function to handle database setup and start the game."""
    db_url = "sqlite:///blackjack.db"
    engine = get_db_engine(db_url)
    init_db(engine)
    Session = sessionmaker(bind=engine)
    
    with Session() as session:
        while True:
            action = get_user_input("Enter 'play' to start a new game, 'view' to view past outcomes, or 'quit' to exit: ")
            if action == "play":
                blackjack_game(session)
            elif action == "view":
                view_game_outcomes(session)
            elif action == "quit":
                console.print("Goodbye!")
                break
            else:
                console.print("Invalid input. Please try again.", style="bold red")

if __name__ == "__main__":
    main()