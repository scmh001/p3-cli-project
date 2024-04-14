import random
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from prompt_toolkit import prompt
from ascii import deck_of_cards
from instructions import header, instructions
<<<<<<< HEAD
from betting import place_bets
=======
from config import SUITS, RANKS, VALUES
from database import get_db_engine, init_db, Player, GameSession
from sqlalchemy.orm import sessionmaker
>>>>>>> 243c9104a69773de2e0b6b455d6e6dbfee46e0bf

console = Console()

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

<<<<<<< HEAD
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
=======
def record_game_session(session, player_id, dealer_hand, player_hand, outcome):
>>>>>>> 243c9104a69773de2e0b6b455d6e6dbfee46e0bf
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
<<<<<<< HEAD
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
            print(f'Looks like we haven\'t seen you before, we\'ll start you out with the max buy in of $100.')
            
            
        if  1 <= money_bag <= 300:
            
            place_bets(20, player_id, get_player_money_bag, update_player_money_bag)
            
            # print("Max table bet is $20:")
            # bet_input = prompt("Please place your bet a number value less than or equal to $20:").strip()
            # bet = int(bet_input)
            # #########NEED TO FILTER INCORRECT BETS  ALL OF THIS COULD BE A HELPER METHOD
            # new_bag = get_player_money_bag(player_id) - bet
            # update_player_money_bag(player_id, new_bag)
            
        elif 301 <= money_bag <= 750:
            
            place_bets(50, player_id, get_player_money_bag, update_player_money_bag)
            
            # print("Max table bet is $50:")
            # bet_input = prompt("Please place your bet a number value less than or equal to $50:").strip()
            # bet = int(bet_input)
            # new_bag = get_player_money_bag(player_id) - bet
            # update_player_money_bag(player_id, new_bag)
            
        elif 751 <= money_bag <= 1000:
            
            place_bets(100, player_id, get_player_money_bag, update_player_money_bag)
            
            # print("Max table bet is $100:")
            # bet_input = prompt("Please place your bet a number value less than or equal to $100:").strip()
            # bet = int(bet_input)
            # new_bag = get_player_money_bag(player_id) - bet
            # update_player_money_bag(player_id, new_bag)
            
        elif 1001 <= money_bag <= 10000:
            
            place_bets(500, player_id, get_player_money_bag, update_player_money_bag)
            
            
            # print("Max table bet is $500:")
            # bet_input = prompt("Please place your bet a number value less than or equal to $500:").strip()
            # bet = int(bet_input)
            # new_bag = get_player_money_bag(player_id) - bet
            # update_player_money_bag(player_id, new_bag)
        elif 10000 <= money_bag:
            
            place_bets(1000, player_id, get_player_money_bag, update_player_money_bag)
            
               
        deck = create_deck()
        shuffle_deck(deck)

        player_hand = [deal_card(deck), deal_card(deck)]
        dealer_hand = [deal_card(deck), deal_card(deck)]

        display_hand(player_hand, "Player")
        display_hand(dealer_hand, "Dealer")
        
        if calculate_hand_value(player_hand) == 21:
            print(f'{header}')
            print(f"Player wins ${bet}!")
            new_bag  = get_player_money_bag(player_id) + (2.5 * bet)
            update_player_money_bag(player_id, new_bag)
            print(f"Total money: ${get_player_money_bag(player_id)}")
            outcome = "Win"

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
            
=======
        user_input = prompt(prompt_text).strip().lower()
        if user_input:
            return user_input
>>>>>>> 243c9104a69773de2e0b6b455d6e6dbfee46e0bf
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

<<<<<<< HEAD
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
=======
def play_game(session) -> None:
    """Handles the game logic for a single game of blackjack."""
    deck = create_deck()
    shuffle_deck(deck)
>>>>>>> 243c9104a69773de2e0b6b455d6e6dbfee46e0bf

    player_hand = [deal_card(deck), deal_card(deck)]
    dealer_hand = [deal_card(deck), deal_card(deck)]

    display_hand(player_hand, "Player")
    display_hand(dealer_hand, "Dealer")

    while calculate_hand_value(player_hand) < 21:
        action = get_user_input("Do you want to hit or stand? ")
        if action == "hit":
            player_hand.append(deal_card(deck))
            display_hand(player_hand, "Player")
        elif action == "stand":
            break

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

<<<<<<< HEAD
=======
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

>>>>>>> 243c9104a69773de2e0b6b455d6e6dbfee46e0bf
if __name__ == "__main__":
    main()