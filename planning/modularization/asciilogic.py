from rich.console import Console
from config import deck_of_cards

console = Console()

def display_hand(hand, player, hide_dealer_card=False):
    console.print(f"{player}'s hand:")
    card_names = []
    ascii_arts = []
    for i, card in enumerate(hand.cards):
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

    console.print(f"Value: {hand.calculate_value()}\n")