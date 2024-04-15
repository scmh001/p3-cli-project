from instructions import header, instructions
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


class BlackjackForm(npyscreen.ActionForm):
    def create(self):
        self.instructions_field = self.add(npyscreen.MultiLineEdit, 
            value=header + "\n\n" + instructions,
            max_height=10, editable=False, relx=1, rely=4, 
            name="Instructions:")
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
        
        print(header)
        print(instructions)
        self.addForm("MAIN", BlackjackForm)


def main():
    BlackjackApp().run()


if __name__ == "__main__":
    main()
    
    
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # -------------------------------------------------------------------
    # -----------------------production with sound feature---------------------------
    
    import os
import random
import openai
import os
import pygame
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

def get_play_suggestion(state: dict) -> str:
    """Get play suggestion from GPT-3."""
    prompt_text = f"Given the current game state:\nPlayer hand: {state['player_hand']}\nDealer hand: {state['dealer_hand']}\nShould I hit or stand?"
    response = openai.Completion.create(
        model="davinci-002",
        prompt=prompt_text,
        temperature=0.1,
        max_tokens=50
    )
    suggestion = response.choices[0].text.strip()
    return suggestion

def play_sound(file_path: str):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


def play_card_draw_sound():
    """Plays the sound effect for drawing a card."""
    play_sound("assets/cardsounds/card-sounds-35956.wav")

def play_shuffle_sound():
    """Plays the sound effect for shuffling the deck."""
    play_sound("assets/cardsounds/shuffle-cards-46455.wav")
    
def play_win_sound():
    """Plays a victory sound"""
    play_sound("assets/cardsounds/success-1-6297.wav")
    
def play_loss_sound():
    """Plays a loss buzzer"""
    play_sound("assets/cardsounds/wrong-buzzer-6268.wav")
    
def create_deck() -> List[Dict[str, str]]:
    """Creates a deck of 52 cards."""
    return [{'suit': suit, 'rank': rank} for suit in SUITS for rank in RANKS]

def shuffle_deck(deck: List[Dict[str, str]]) -> None:
    """Shuffles the deck in place."""
    play_shuffle_sound()
    random.shuffle(deck)
    

def deal_card(deck: List[Dict[str, str]]) -> Dict[str, str]:
    """Deals a card from the deck."""
    play_card_draw_sound()
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
        play_loss_sound()
        console.print("Player busts! Dealer wins.")
        return "Loss"
    elif dealer_hand_value > 21:
        play_win_sound()
        console.print("Dealer busts! Player wins.")
        return "Win"
    elif player_hand_value > dealer_hand_value:
        play_win_sound()
        console.print("Player wins!")
        return "Win"
    elif player_hand_value < dealer_hand_value:
        play_loss_sound()
        console.print("Dealer wins!")
        return "Loss"
    else:
        play_loss_sound()
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