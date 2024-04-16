import os
import random
import openai
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from prompt_toolkit import prompt
from sqlalchemy.orm import sessionmaker
from ascii import deck_of_cards
from betting import place_bets, table_bets
from config import RANKS, SUITS, VALUES, HEADER, INSTRUCTIONS
from models import GameSession, Player, get_db_engine, init_db
from dotenv import load_dotenv

console = Console()

def configure() -> None:
    """Load environment variables from .env file and configure OpenAI API key."""
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

def get_play_suggestion(player_hand: List[Dict[str, str]], dealer_hand: List[Dict[str, str]]) -> str:
    """Get a play suggestion from the OpenAI API based on the current game state."""
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

def create_deck() -> List[Dict[str, str]]:
    """Create a standard 52-card deck."""
    return [{"suit": suit, "rank": rank} for suit in SUITS for rank in RANKS]

def shuffle_deck(deck: List[Dict[str, str]]) -> None:
    """Shuffle the deck in-place."""
    random.shuffle(deck)

def deal_card(deck: List[Dict[str, str]]) -> Dict[str, str]:
    """Deal a single card from the deck."""
    return deck.pop()

def calculate_hand_value(hand: List[Dict[str, str]]) -> int:
    """Calculate the value of a hand."""
    value = sum(VALUES[card["rank"]] for card in hand)
    aces = sum(card["rank"] == "Ace" for card in hand)
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

def display_hand(hand: List[Dict[str, str]], player: str, hide_dealer_card: bool = False) -> None:
    """Display a player's hand using ASCII art."""
    console.print(f"{player}'s hand:")
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

def get_or_create_player(session, name: str) -> Player:
    """Get or create a player by name."""
    player = session.query(Player).filter_by(name=name).first()
    if not player:
        player = Player(name=name)
        session.add(player)
        session.commit()
    return player

def get_player_money_bag(session, player_id: int) -> int:
    """Get a player's current money bag amount."""
    player = session.query(Player).filter_by(id=player_id).first()
    return player.money_bag if player else None

def update_player_money_bag(session, player_id: int, new_amount: int) -> None:
    """Update a player's money bag amount."""
    player = session.query(Player).filter_by(id=player_id).first()
    if player:
        player.money_bag = new_amount
        session.commit()
    else:
        raise Exception("Player not found")

def record_game_session(session, player_id: int, dealer_hand: List[Dict[str, str]], 
                        player_hand: List[Dict[str, str]], outcome: str) -> None:
    """Record a game session in the database."""
    game_session = GameSession(
        player_id=player_id,
        dealer_hand_value=calculate_hand_value(dealer_hand),
        player_hand_value=calculate_hand_value(player_hand),
        outcome=outcome,
    )
    session.add(game_session)
    session.commit()

def get_user_input(prompt_text: str) -> str:
    """Get user input with validation."""
    while True:
        user_input = prompt(prompt_text).strip().lower()
        if user_input:
            return user_input
        console.print("Invalid input. Please try again.", style="bold red")

def computer_play(deck: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Simulate a computer player's turn."""
    hand = []
    while calculate_hand_value(hand) < 17:
        hand.append(deal_card(deck))
    return hand

def play_game(session, players, bet):
    """Play a single game of Blackjack."""
    os.system("clear")
    deck = create_deck()
    shuffle_deck(deck)

    dealer_hand = [deal_card(deck), deal_card(deck)]
    player_hands = {player.id: [deal_card(deck), deal_card(deck)] for player in players}
    
    display_hand(dealer_hand, "Dealer", hide_dealer_card=True)
    for player in players:
        display_hand(player_hands[player.id], player.name)

    for player in players:
        player_id = player.id
        player_hand = player_hands[player_id]

        if calculate_hand_value(player_hand) == 21:
            console.print(f"{player.name} has Blackjack!")
            new_amount = get_player_money_bag(session, player_id) + (2.5 * bet)
            update_player_money_bag(session, player_id, new_amount)
            record_game_session(session, player_id, dealer_hand, player_hand, "Win")
            continue

        while calculate_hand_value(player_hand) < 21:
            if player.name != "Computer":
                action = get_user_input(f"{player.name}, do you want to hit, stand or get help? ")
            else:
                action = "stand" if calculate_hand_value(player_hand) >= 17 else "hit"
                console.print(f"Computer {player.name} chooses to {action}")

            if action == "hit":
                player_hand.append(deal_card(deck))
                display_hand(player_hand, player.name)
            elif action == "stand":
                break
            elif action == "help":
                suggestion = get_play_suggestion(player_hand, dealer_hand)
                console.print("Suggested play:", style="bold green")
                console.print(suggestion)

        player_hands[player_id] = player_hand

    console.print("Revealing Dealer's Hand...")
    display_hand(dealer_hand, "Dealer")

    while calculate_hand_value(dealer_hand) < 17:
        dealer_hand.append(deal_card(deck))
        display_hand(dealer_hand, "Dealer")

    dealer_hand_value = calculate_hand_value(dealer_hand)

    for player in players:
        player_id = player.id
        player_hand = player_hands[player_id]
        player_hand_value = calculate_hand_value(player_hand)

        if player_hand_value > 21:
            console.print(f"{player.name} busts!")
            outcome = "Loss"
        elif dealer_hand_value > 21:
            console.print(f"Dealer busts! {player.name} wins.")
            new_amount = get_player_money_bag(session, player_id) + (2 * bet)
            update_player_money_bag(session, player_id, new_amount)
            outcome = "Win"
        elif player_hand_value > dealer_hand_value:
            console.print(f"{player.name} wins!")
            new_amount = get_player_money_bag(session, player_id) + (2 * bet)
            update_player_money_bag(session, player_id, new_amount)
            outcome = "Win"
        elif player_hand_value < dealer_hand_value:
            console.print(f"{player.name} loses.")
            outcome = "Loss"
        else:
            console.print(f"{player.name} ties with the dealer.")
            outcome = "Tie"

        record_game_session(session, player_id, dealer_hand, player_hand, outcome)
        
        
def blackjack_game(session):
    """Play multiple games of Blackjack."""
    console.print(HEADER)
    console.print(INSTRUCTIONS)

    num_computer_players = int(get_user_input("Enter the number of computer players (0-2): "))
    if num_computer_players not in [0, 1, 2]:
        console.print("Invalid number of computer players. Defaulting to 0.", style="bold red")
        num_computer_players = 0

    players = []
    for i in range(num_computer_players):
        computer_player = get_or_create_player(session, f"Computer {i+1}")
        players.append(computer_player)

    while True:
        player_name = get_user_input("Please enter your player name (or 'quit' to exit): ")
        if player_name == "quit":
            console.print("Thanks for playing!")
            break

        human_player = get_or_create_player(session, player_name)
        players.append(human_player)

        bet = int(get_user_input("Enter your bet amount: "))
        play_game(session, players, bet)

        players.remove(human_player)

        play_again = get_user_input("Do you want to play again? (yes/no): ")
        if play_again != "yes":
            console.print("Thanks for playing!")
            break

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
                break
            else:
                console.print("Invalid input. Please try again.", style="bold red")

if __name__ == "__main__":
    main()