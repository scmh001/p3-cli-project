from prompt_toolkit import prompt
from rich.console import Console

console = Console()

def place_bets(session, max_bet, player_id, function_one, function_two):
    while True:
        try:
            print(f"Max table bet is {max_bet}:")
            bet_input = prompt(f"Please place your bet a number up to {max_bet}: ").strip()
            bet = int(bet_input)
            if bet < 1 or bet > max_bet:
                print(f"Please enter a valid bet amount from $1 to ${max_bet}.")
                continue
            current_money_bag = function_one(session, player_id)
            if bet > current_money_bag:
                print(f'You cannot bet more than your current funds: {current_money_bag}. Please try again')
                continue
            new_bag = current_money_bag - bet
            function_two(session, player_id, new_bag)
            return bet
        except ValueError:
            print("Invalid input. Please enter a numerical value.")

def get_max_bet(money_bag):
    max_bet_ranges = [
        (1, 250, 20),
        (251, 500, 50),
        (501, 1000, 100),
        (1001, 5000, 250),
        (5001, 10000, 500),
        (10001, float('inf'), 1000)
    ]
    for min_range, max_range, max_bet in max_bet_ranges:
        if min_range <= money_bag <= max_range:
            return max_bet
    return 0

def table_bets(session, player_id, money_bag, get_player_money_bag, update_player_money_bag):
    max_bet = get_max_bet(money_bag)
    print(f"You currently have ${money_bag}.")
    place_bets(session, max_bet, player_id, get_player_money_bag, update_player_money_bag)