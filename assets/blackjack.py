import os
import random
import openai
import pygame
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from prompt_toolkit import prompt
from sqlalchemy.orm import sessionmaker
from ascii import deck_of_cards
from betting import place_bets, table_bets
from config import RANKS, SUITS, VALUES, header, instructions
from models import (GameSession, Player, get_db_engine, init_db)
from dotenv import load_dotenv
from play_sound import play_card_draw_sound,play_loss_sound, play_shuffle_sound, play_win_sound, play_again_sound, play_start_sound

console = Console()



# Configure environment variables and OpenAI API key
def configure() -> None:
    """
    Load environment variables from .env file and configure OpenAI API key.
    This function is called at the start of the program to set up the required
    configuration before running the game.
    """
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

# Get play suggestion from OpenAI based on game state 
def get_play_suggestion(state: Dict[str, List[Dict[str, str]]]) -> str:
    """
    Get a play suggestion from OpenAI's GPT-3.5-turbo model based on the current game state.
    
    Args:
        state (Dict[str, List[Dict[str, str]]]): A dictionary representing the current game state,
            including the player's hand and the dealer's hand.
            
    Returns:
        str: The suggested play action (e.g., "hit" or "stand") based on the game state.
    """
    prompt_text = (
        f"Given the current game state:\n"
        f"Player hand: {player_hand}\n"
        f"Dealer hand: {dealer_hand}\n"
        f"Should I hit or stand?"
    )
    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt_text,
        temperature=0.1,
        max_tokens=50,
    )
    return response.choices[0].text.strip()

# Create a new deck of cards
def create_deck() -> List[Dict[str, str]]:
    """
    Create a new standard deck of 52 playing cards.
    
    Returns:
        List[Dict[str, str]]: A list of dictionaries representing each card in the deck,
            where each dictionary contains the 'suit' and 'rank' of the card.
    """
    return [{"suit": suit, "rank": rank} for suit in SUITS for rank in RANKS]

# Shuffle the deck of cards
def shuffle_deck(deck: List[Dict[str, str]]) -> None:
    play_shuffle_sound()
    """
    Shuffle the given deck of cards in-place using the Fisher-Yates shuffle algorithm.
    
    Args:
        deck (List[Dict[str, str]]): The deck of cards to be shuffled.
    """
    random.shuffle(deck)

# Deal a card from the deck
def deal_card(deck: List[Dict[str, str]]) -> Dict[str, str]:
    play_card_draw_sound()
    """
    Deal a single card from the top of the deck.
    
    Args:
        deck (List[Dict[str, str]]): The deck of cards to deal from.
        
    Returns:
        Dict[str, str]: A dictionary representing the dealt card, containing its 'suit' and 'rank'.
    """
    return deck.pop()

# Calculate the value of a hand of cards
def calculate_hand_value(hand: List[Dict[str, str]]) -> int:
    """
    Calculate the total value of a hand of cards according to standard blackjack rules.
    
    Args:
        hand (List[Dict[str, str]]): The hand of cards to calculate the value for.
        
    Returns:
        int: The total value of the hand.
    """
    value = sum(VALUES[card["rank"]] for card in hand)
    aces = sum(card["rank"] == "Ace" for card in hand)
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

# Display a hand of cards
def display_hand(
    hand: List[Dict[str, str]],
    player: str,
    hide_dealer_card: bool = False,
    calculate_value: bool = True,
) -> None:
    """
    Display a hand of cards using ASCII art and optionally calculate and display the hand's value.
    
    Args:
        hand (List[Dict[str, str]]): The hand of cards to display.
        player (str): The name of the player who holds the hand.
        hide_dealer_card (bool, optional): Whether to hide the dealer's second card. Defaults to False.
        calculate_value (bool, optional): Whether to calculate and display the hand's value. Defaults to True.
    """
    console.print(f"[bold blue]{player}'s hand:[/bold blue]")
    card_names = []
    ascii_arts = []
    for i, card in enumerate(hand):
        if hide_dealer_card and player == "Dealer" and i == 1:
            card_name = "Hidden"
            ascii_art = deck_of_cards["Card Back"].split("\n")
        else:
            card_name = f"{card['rank']} of {card['suit']}"
            ascii_art = deck_of_cards.get(card_name, "Card not found").split("\n")
        
        console.print(card_name.center(len(ascii_art[0])))
        for line in ascii_art:
            console.print(line)
    
    if not hide_dealer_card:
        console.print(f"Value: {calculate_hand_value(hand)}\n")

# Get or create a player in the database
def get_or_create_player(session, name: str) -> Player:
    """
    Retrieve a player from the database by name, or create a new player if not found.
    
    Args:
        session: The SQLAlchemy database session.
        name (str): The name of the player to retrieve or create.
        
    Returns:
        Player: The retrieved or newly created player object.
    """
    player = session.query(Player).filter_by(name=name).first()
    if player is None:
        player = Player(name=name)
        session.add(player)
        session.commit()
    return player

# Get a player's money bag amount from the database
def get_player_money_bag(session, player_id: int) -> int:
    """
    Retrieve the money bag amount for a player from the database.
    
    Args:
        session: The SQLAlchemy database session.
        player_id (int): The ID of the player to retrieve the money bag amount for.
        
    Returns:
        int: The player's money bag amount, or None if the player is not found.
    """
    player = session.query(Player).filter_by(id=player_id).first()
    return player.money_bag if player else None

# Update a player's money bag amount in the database
def update_player_money_bag(session, player_id: int, new_amount: int) -> None:
    """
    Update a player's money bag amount in the database.
    
    Args:
        session: The SQLAlchemy database session.
        player_id (int): The ID of the player to update the money bag amount for.
        new_amount (int): The new money bag amount to set for the player.
        
    Raises:
        Exception: If the player is not found in the database.
    """
    player = session.query(Player).filter_by(id=player_id).first()
    if player:
        player.money_bag = new_amount
        session.commit()
    else:
        raise Exception("Player not found")

# Record a game session in the database
def record_game_session(
    session,
    player_id: int,
    dealer_hand: List[Dict[str, str]],
    player_hand: List[Dict[str, str]],
    outcome: str,
) -> None:
    """
    Record a completed game session in the database.
    
    Args:
        session: The SQLAlchemy database session.
        player_id (int): The ID of the player who played the game.
        dealer_hand (List[Dict[str, str]]): The dealer's hand at the end of the game.
        player_hand (List[Dict[str, str]]): The player's hand at the end of the game.
        outcome (str): The outcome of the game (e.g., "Win", "Loss", "Tie").
    """
    game_session = GameSession(
        player_id=player_id,
        dealer_hand_value=calculate_hand_value(dealer_hand),
        player_hand_value=calculate_hand_value(player_hand),
        outcome=outcome,
    )
    session.add(game_session)
    session.commit()

# Get user input with validation
def get_user_input(prompt_text: str, allow_empty=False) -> str:
    # """
    # Prompt the user for input and validate the input.
    
    # Args:
    #     prompt_text (str): The text to display as the prompt to the user.
        
    # Returns:
    #     str: The user's input, stripped of leading/trailing whitespace.
    # """
    # while True:
    #     user_input = prompt(prompt_text).strip().lower()
    #     if user_input:
    #         return user_input
    #     console.print("Invalid input. Please try again.", style="bold red")
        
        while True:
            user_input = input(prompt_text).strip().lower()
            if user_input or allow_empty:
                return user_input
            console.print("Invalid input. Please try again.", style="bold red")

# Play a game of blackjack
def play_game(session, player: Player) -> None:
    """
    Play a single game of blackjack.
    
    Args:
        session: The SQLAlchemy database session.
        player (Player): The player object representing the user playing the game.
    """
    os.system("clear")
    deck = create_deck()
    player_id = player.id
    current_money = get_player_money_bag(session, player_id)
    
    # Extend credit if player is out of money
    if current_money < 1:
        print("Sorry you've had a string of bad luck. We're extending you $100 in credit.")
        update_player_money_bag(session, player_id, 100)
        current_money = 100
        prompt("Press enter to continue")
    
    # Place bets
    bet = table_bets(session, player_id, current_money, get_player_money_bag, update_player_money_bag)
        
    shuffle_deck(deck)

    dealer_hand = [deal_card(deck), deal_card(deck)]

    # display_hand(dealer_hand, "Dealer", hide_dealer_card=True, calculate_value=False)
    # display_hand(player_hand, "Player")
    
    display_hand([dealer_hand[0], {"rank": "Hidden", "suit": ""}], "Dealer", hide_dealer_card=True, calculate_value=False)
    display_hand(player_hand, "Player", hide_dealer_card=False, calculate_value=True)
    
    # Check for blackjack
    if calculate_hand_value(player_hand) == 21 and calculate_hand_value(dealer_hand) < 21:
        print(f"{header}")
        print("You won!")
        new_amount = get_player_money_bag(session, player_id) + (2.5 * bet)
        update_player_money_bag(session, player_id, new_amount)
        return dealer_hand, player_hand, "Win"

    # Player's turn
    # while calculate_hand_value(player_hand) < 21:
    #     action = get_user_input("Do you want to hit, stand or get help? ")
    #     if action == "hit":
    #         os.system("clear")
    #         player_hand.append(deal_card(deck))
    #         display_hand(player_hand, "Player")
    #         display_hand(dealer_hand, "Dealer")
    #     elif action == "stand":
    #         break
    #     elif action == "help":
    #         suggestion = get_play_suggestion(
    #             {"player_hand": player_hand, "dealer_hand": dealer_hand}
    #         )
    #         console.print("Suggested play:", style="bold green")
    #         console.print(suggestion)
    
    
    while calculate_hand_value(player_hand) < 21:
        action = get_user_input("Do you want to hit, stand or get help? ")
        if action == "hit":
            player_hand.append(deal_card(deck))
            os.system("clear")
            display_hand([dealer_hand[0], {"rank": "Hidden", "suit": ""}], "Dealer", hide_dealer_card=True, calculate_value=False)
            display_hand(player_hand, "Player")
        elif action == "stand":
            break
        elif action == "help":
            suggestion = get_play_suggestion(
                {"player_hand": player_hand, "dealer_hand": dealer_hand}
            )
            console.print("Suggested play:", style="bold green")
            console.print(suggestion)
    

    console.print("Revealing Dealer's Hand...")
    display_hand(dealer_hand, "Dealer", hide_dealer_card=False, calculate_value=True)
    while calculate_hand_value(dealer_hand) < 17:
        dealer_hand.append(deal_card(deck))
        display_hand(dealer_hand, "Dealer", hide_dealer_card=False, calculate_value=True)

    dealer_hand_value = calculate_hand_value(dealer_hand)
    
    # Determine winner
    if player_hand_value > 21:
        play_loss_sound()
        console.print("Player busts! Dealer wins.")
        outcome = "Loss"
    elif dealer_hand_value > 21:
        play_win_sound()
        console.print("Dealer busts! Player wins.")
        new_amount = get_player_money_bag(session, player_id) + (2 * bet)
        update_player_money_bag(session, player_id, new_amount)
        outcome = "Win"     
    elif player_hand_value > dealer_hand_value:
        play_win_sound()
        new_amount = get_player_money_bag(session, player_id) + (2 * bet)
        update_player_money_bag(session, player_id, new_amount)
        console.print("Player wins!")
        outcome = "Win"
    elif player_hand_value < dealer_hand_value:
        play_loss_sound()
        console.print("Dealer wins!")
        outcome = "Loss"
    else:
        console.print("It's a tie!")
        play_loss_sound()
        new_amount = get_player_money_bag(session, player_id) + (bet)
        update_player_money_bag(session, player_id, new_amount)
        outcome = "Tie"
        
    play_again_sound()
    
    return dealer_hand, player_hand, outcome
    

# Main blackjack game loop
def blackjack_game(session) -> None:
    # """
    # The main game loop for playing multiple rounds of blackjack.
    
    # Args:
    #     session: The SQLAlchemy database session.
    # """
    # os.system("clear")
    # console.print(header)
    # console.print(instructions)
    # play_start_sound()
    
    # while True:
    #     os.system("clear")
    #     player_name = get_user_input("Please enter your player name: ")
    #     player = get_or_create_player(session, player_name)
    #     dealer_hand, player_hand, outcome = play_game(session, player)
    #     record_game_session(session, player.id, dealer_hand, player_hand, outcome)

    #     play_again = get_user_input("Do you want to play again? (yes/no): ")
    #     if play_again != "yes":
    #         os.system("clear")
    #         console.print("Thanks for playing!")
    #         break
    
    os.system("clear")
    console.print(header)
    console.print(instructions)
    play_start_sound()
    
    # Initial setup: Get the player's name only once
    player_name = get_user_input("Please enter your player name: ", allow_empty=False)
    player = get_or_create_player(session, player_name)

    while True:
        os.system("clear")
        console.print(f"Welcome back, {player_name}!")

        # Start a new game with the existing player object
        dealer_hand, player_hand, outcome = play_game(session, player)
        record_game_session(session, player.id, dealer_hand, player_hand, outcome)

        # Ask the user if they want to play again
        play_again = get_user_input("Press Enter to play again or type 'no' to exit: ", allow_empty=True)
        if play_again.lower() == "no":
            os.system("clear")
            console.print("Thanks for playing!")
            break
     

# View past game outcomes
def view_game_outcomes(session) -> None:
    """View past game outcomes."""
    query = (
        session.query(
            GameSession.player_id,
            Player.name,
            GameSession.dealer_hand_value,
            GameSession.player_hand_value,
            GameSession.outcome,
        )
        .join(Player)
    )

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
            game_session.outcome,
        )

    console.print(table)

# Main program entry point
def main() -> None:
    """Main function to run the Blackjack game."""
    configure()
    db_url = "sqlite:///blackjack.db"
    engine = get_db_engine(db_url)
    init_db(engine)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        
        while True:
            action = get_user_input(
                "Enter 'play' to start a new game, 'view' to view past outcomes, or 'quit' to exit: "
            )
            if action == "play":
                blackjack_game(session)
            elif action == "view":
                view_game_outcomes(session)
            elif action == "quit":
                console.print("Goodbye!")
                os.system("clear")
                break
            else:
                console.print("Invalid input. Please try again.", style="bold red")

# Run the main program
if __name__ == "__main__":
    main()