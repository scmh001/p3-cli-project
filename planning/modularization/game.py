import os
from rich.console import Console
from deck import Deck
from hand import Hand
from player import Player
from db import get_player_money_bag, update_player_money_bag, record_game_session
from ai import get_play_suggestion
from asciilogic import display_hand
from bettinglogic import table_bets

console = Console()

def get_user_input(prompt_text: str) -> str:
    while True:
        user_input = input(prompt_text).strip().lower()
        if user_input:
            return user_input
        console.print("Invalid input. Please try again.", style="bold red")

def play_game(session, player: Player) -> None:
    os.system("clear")
    deck = Deck()
    player_id = player.id
    current_money = get_player_money_bag(session, player_id)
    
    if current_money < 1:
        print("Sorry you've had a string of bad luck. We're extending you $100 in credit.")
        update_player_money_bag(session, player_id, 100)
        input("Press enter to continue")
    
    bet = table_bets(session, player_id, current_money, get_player_money_bag, update_player_money_bag)
        
    deck.shuffle()

    player_hand = Hand()
    player_hand.add_card(deck.deal_card())
    player_hand.add_card(deck.deal_card())
    
    dealer_hand = Hand() 
    dealer_hand.add_card(deck.deal_card())
    dealer_hand.add_card(deck.deal_card())

    display_hand(dealer_hand, "Dealer", hide_dealer_card=True)
    display_hand(player_hand, "Player")
    
    if player_hand.calculate_value() == 21 and dealer_hand.calculate_value() < 21:
        print("You won!")
        new_amount = get_player_money_bag(session, player_id) + (2.5 * bet)
        update_player_money_bag(session, player_id, new_amount)
        return dealer_hand, player_hand, "Win"

    while player_hand.calculate_value() < 21:
        action = get_user_input("Do you want to hit, stand or get help? ")
        if action == "hit":
            os.system("clear")
            player_hand.add_card(deck.deal_card())
            display_hand(player_hand, "Player")
            display_hand(dealer_hand, "Dealer")
        elif action == "stand":
            break
        elif action == "help":
            suggestion = get_play_suggestion(
                {"player_hand": player_hand.cards, "dealer_hand": dealer_hand.cards}
            )
            console.print("Suggested play:", style="bold green")
            console.print(suggestion)

    console.print("Revealing Dealer's Hand...")
    display_hand(dealer_hand, "Dealer")

    player_hand_value = player_hand.calculate_value()
    dealer_hand_value = dealer_hand.calculate_value()
    
    if player_hand_value > 21:
        console.print("Player busts! Dealer wins.")
        outcome = "Loss"
    elif dealer_hand_value > 21:
        console.print("Dealer busts! Player wins.")
        new_amount = get_player_money_bag(session, player_id) + (2 * bet)
        update_player_money_bag(session, player_id, new_amount)
        outcome = "Win"     
    elif player_hand_value > dealer_hand_value:
        new_amount = get_player_money_bag(session, player_id) + (2 * bet)
        update_player_money_bag(session, player_id, new_amount)
        console.print("Player wins!")
        outcome = "Win"
    elif player_hand_value < dealer_hand_value:
        console.print("Dealer wins!")
        outcome = "Loss"
    else:
        console.print("It's a tie!")
        outcome = "Tie"
      
    return dealer_hand, player_hand, outcome