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
from config import RANKS, SUITS, VALUES, header, instructions
from database import (GameSession, Player, get_db_engine, init_db)
from dotenv import load_dotenv
from outcomes import view_game_outcomes

console = Console()


def configure() -> None:
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")


def get_play_suggestion(state: Dict[str, List[Dict[str, str]]]) -> str:
    prompt_text = (
        f"Given the current game state:\n"
        f"Player hand: {state['player_hand']}\n"
        f"Dealer hand: {state['dealer_hand']}\n"
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
    return [{"suit": suit, "rank": rank} for suit in SUITS for rank in RANKS]


def shuffle_deck(deck: List[Dict[str, str]]) -> None:
    random.shuffle(deck)


def deal_card(deck: List[Dict[str, str]]) -> Dict[str, str]:
    return deck.pop()


def calculate_hand_value(hand: List[Dict[str, str]]) -> int:
    value = sum(VALUES[card["rank"]] for card in hand)
    aces = sum(card["rank"] == "Ace" for card in hand)
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value


def display_hand(
    hand: List[Dict[str, str]],
    player: str,
    hide_dealer_card: bool = False,
    calculate_value: bool = True,
) -> None:
    console.print(f"{player}'s hand:")
    card_names = []
    ascii_arts = []
    for i, card in enumerate(hand):
        if hide_dealer_card and player == "Dealer" and i == 1:
            card_name = "Hidden"
            ascii_art = deck_of_cards["Card Back"].split("\n")
        else:
            card_name = f"{card['rank']} of {card['suit']}"
            ascii_art = deck_of_cards.get(card_name, "Card not found").split("\n")
        card_names.append(card_name)
        ascii_arts.append(ascii_art)

    max_height = max(len(art) for art in ascii_arts)

    for card_name in card_names:
        console.print(card_name.center(len(ascii_arts[0])))

    for row in range(max_height):
        for ascii_art in ascii_arts:
            if row < len(ascii_art):
                console.print(ascii_art[row], end=" ")
            else:
                console.print(" " * len(ascii_art[0]), end=" ")
        console.print()

    if calculate_value:
        console.print(f"Value: {calculate_hand_value(hand)}\n")


def get_or_create_player(session, name: str) -> Player:
    player = session.query(Player).filter_by(name=name).first()
    if not player:
        player = Player(name=name)
        session.add(player)
        session.commit()
    return player


def get_player_money_bag(session, player_id: int) -> int:
    player = session.query(Player).filter_by(id=player_id).first()
    return player.money_bag if player else None


def update_player_money_bag(session, player_id: int, new_amount: int) -> None:
    player = session.query(Player).filter_by(id=player_id).first()
    if player:
        player.money_bag = new_amount
        session.commit()
    else:
        raise Exception("Player not found")


def record_game_session(
    session,
    player_id: int,
    dealer_hand: List[Dict[str, str]],
    player_hand: List[Dict[str, str]],
    outcome: str,
) -> None:
    game_session = GameSession(
        player_id=player_id,
        dealer_hand_value=calculate_hand_value(dealer_hand),
        player_hand_value=calculate_hand_value(player_hand),
        outcome=outcome,
    )
    session.add(game_session)
    session.commit()


def get_user_input(prompt_text: str) -> str:
    while True:
        user_input = prompt(prompt_text).strip().lower()
        if user_input:
            return user_input
        console.print("Invalid input. Please try again.", style="bold red")


def computer_play(hand: List[Dict[str, str]], deck: List[Dict[str, str]]) -> List[Dict[str, str]]:
    while calculate_hand_value(hand) < 17:
        hand.append(deal_card(deck))
    return hand


def play_game(session, player: Player, num_computer_players: int) -> None:
    os.system("clear")
    deck = create_deck()
    player_id = player.id
    current_money = get_player_money_bag(session, player_id)
    
    if current_money < 1:
        print("Sorry you've had a string of bad luck. We're extending you $100 in credit.")
        update_player_money_bag(session, player_id, 100)
        prompt("Press enter to continue")
    
    bet = table_bets(session, player_id, current_money, get_player_money_bag, update_player_money_bag)
        
    shuffle_deck(deck)

    player_hand = [deal_card(deck), deal_card(deck)]
    dealer_hand = [deal_card(deck), deal_card(deck)]
    computer_hands = [[deal_card(deck), deal_card(deck)] for _ in range(num_computer_players)]

    display_hand(dealer_hand, "Dealer", hide_dealer_card=True, calculate_value=False)
    display_hand(player_hand, "Player")
    for i, hand in enumerate(computer_hands, 1):
        display_hand(hand, f"Computer {i}")
    
    if calculate_hand_value(player_hand) == 21 and calculate_hand_value(dealer_hand) < 21:
        print(f"{header}")
        print("You won!")
        new_amount = get_player_money_bag(session, player_id) + (2.5 * bet)
        update_player_money_bag(session, player_id, new_amount)
        return dealer_hand, player_hand, "Win"

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
            suggestion = get_play_suggestion(
                {"player_hand": player_hand, "dealer_hand": dealer_hand}
            )
            console.print("Suggested play:", style="bold green")
            console.print(suggestion)

    for i, hand in enumerate(computer_hands, 1):
        computer_hands[i-1] = computer_play(hand, deck)

    console.print("Revealing Dealer's Hand...")
    display_hand(dealer_hand, "Dealer", calculate_value=True)

    player_hand_value = calculate_hand_value(player_hand)
    dealer_hand_value = calculate_hand_value(dealer_hand)
    computer_hand_values = [calculate_hand_value(hand) for hand in computer_hands]
    
    if player_hand_value > 21:
        console.print("Player busts! Dealer wins.")
        outcome = "Loss"
    elif dealer_hand_value > 21:
        console.print("Dealer busts! Player wins.")
        new_amount = get_player_money_bag(session, player_id) + (2 * bet)
        update_player_money_bag(session, player_id, new_amount)
        outcome = "Win"     
    elif player_hand_value > dealer_hand_value and player_hand_value > max(computer_hand_values):
        new_amount = get_player_money_bag(session, player_id) + (2 * bet)
        update_player_money_bag(session, player_id, new_amount)
        console.print("Player wins!")
        outcome = "Win"
    elif player_hand_value < dealer_hand_value or player_hand_value < max(computer_hand_values):
        console.print("Dealer or computer wins!")
        outcome = "Loss"
    else:
        console.print("It's a tie!")
        outcome = "Tie"
      
    return dealer_hand, player_hand, outcome


def blackjack_game(session) -> None:
    console.print(header)
    console.print(instructions)
    while True:
        player_name = get_user_input("Please enter your player name: ")
        player = get_or_create_player(session, player_name)

        num_computer_players = 0
        while True:
            num_str = get_user_input("Enter number of computer opponents (0-2): ")
            if num_str in ["0", "1", "2"]:
                num_computer_players = int(num_str)
                break
            else:
                console.print("Invalid input. Please enter 0, 1, or 2.", style="bold red")

        dealer_hand, player_hand, outcome = play_game(session, player, num_computer_players)
        record_game_session(session, player.id, dealer_hand, player_hand, outcome)

        play_again = get_user_input("Do you want to play again? (yes/no): ")
        if play_again != "yes":
            console.print("Thanks for playing!")
            break


def view_game_outcomes(session) -> None:
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