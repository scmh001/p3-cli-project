import os
import random
from rich.console import Console
from rich.table import Table
from sqlalchemy.orm import sessionmaker
from models import Player, get_db_engine, init_db

console = Console()

def create_deck(num_decks: int) -> list:
    """Create a new shuffled deck with the specified number of decks."""
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
    deck = [{'suit': suit, 'rank': rank} for _ in range(num_decks) for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck

def deal_card(deck: list) -> dict:
    """Deal a single card from the deck."""
    return deck.pop()

def display_card(card: dict, hide: bool = False) -> None:
    """Display a single card."""
    if hide:
        console.print("[bold white]XX[/bold white]")
    else:
        console.print(f"[bold white]{card['rank']} of {card['suit']}[/bold white]")

def get_hand_value(hand: list) -> int:
    """Calculate the value of a hand."""
    value = sum(10 if card['rank'] in ['10', 'Jack', 'Queen', 'King'] else 11 if card['rank'] == 'Ace' else int(card['rank']) for card in hand)
    num_aces = sum(card['rank'] == 'Ace' for card in hand)
    while value > 21 and num_aces > 0:
        value -= 10
        num_aces -= 1
    return value

def update_count(card: dict, count: int) -> int:
    """Update the running count based on the dealt card."""
    if card['rank'] in ['2', '3', '4', '5', '6']:
        count += 1
    elif card['rank'] in ['10', 'Jack', 'Queen', 'King', 'Ace']:
        count -= 1
    return count

def get_true_count(count: int, remaining_decks: float) -> float:
    """Calculate the true count based on the running count and remaining decks."""
    return count / remaining_decks

def get_user_input(prompt: str) -> str:
    """Get user input with the specified prompt."""
    while True:
        user_input = input(prompt).strip()
        if user_input:
            return user_input
        console.print("Invalid input. Please try again.", style="bold red")

def play_round(deck: list, num_decks: int) -> tuple:
    """Play a single round of card counting training."""
    player_hand = []
    dealer_hand = []
    count = 0

    # Deal initial cards
    for _ in range(2):
        player_card = deal_card(deck)
        player_hand.append(player_card)
        count = update_count(player_card, count)

        dealer_card = deal_card(deck)
        dealer_hand.append(dealer_card)
        count = update_count(dealer_card, count)

    console.print("\nDealer's hand:")
    display_card(dealer_hand[0])
    display_card(None, hide=True)

    console.print("\nPlayer's hand:")
    for card in player_hand:
        display_card(card)

    # Prompt user for running count
    remaining_decks = len(deck) / 52
    true_count = get_true_count(count, remaining_decks)

    user_count = int(get_user_input("Enter the running count: "))
    if user_count == count:
        console.print("Correct count!", style="bold green")
    else:
        console.print(f"Incorrect count. The correct count is {count}.", style="bold red")

    console.print(f"\nTrue count: {true_count:.2f}")

    if true_count >= 2:
        console.print("Recommendation: Increase your bet.", style="bold green")
    elif true_count <= -2:
        console.print("Recommendation: Decrease your bet.", style="bold red")
    else:
        console.print("Recommendation: Maintain your bet.", style="bold yellow")

    return count, true_count

def play_game(session, player: Player, num_decks: int) -> None:
    """Play multiple rounds of card counting training."""
    deck = create_deck(num_decks)
    num_rounds = 0
    total_count = 0
    total_true_count = 0

    while True:
        if len(deck) < num_decks * 52 * 0.25:  # Reshuffle when 75% of cards are dealt
            deck = create_deck(num_decks)
            console.print("\nReshuffling the deck...", style="bold blue")

        count, true_count = play_round(deck, num_decks)
        num_rounds += 1
        total_count += count
        total_true_count += true_count

        play_again = get_user_input("\nPress Enter to continue or type 'quit' to exit: ")
        if play_again.lower() == "quit":
            break

    avg_count = total_count / num_rounds
    avg_true_count = total_true_count / num_rounds

    console.print(f"\nGame summary for {player.name}:", style="bold blue")
    console.print(f"Number of rounds played: {num_rounds}")
    console.print(f"Average running count: {avg_count:.2f}")
    console.print(f"Average true count: {avg_true_count:.2f}")

def main() -> None:
    """Main program entry point."""
    db_url = "sqlite:///blackjack.db"
    engine = get_db_engine(db_url)
    init_db(engine)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        player_name = get_user_input("Enter your name: ")
        player = session.query(Player).filter_by(name=player_name).first()
        if not player:
            player = Player(name=player_name)
            session.add(player)
            session.commit()

        num_decks = int(get_user_input("Enter the number of decks to use (1-8): "))
        play_game(session, player, num_decks)

if __name__ == "__main__":
    main()