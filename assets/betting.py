from prompt_toolkit import prompt
from rich.console import Console

console = Console

def place_bets(session, max_bet, player_id, 
               function_one, function_two):
    while True:
        try:
            print(f"Max table bet is {max_bet}:")
            bet_input = prompt(f"Please place your bet a number up to {max_bet}: ").strip()
            bet = int(bet_input)
            if bet < 1 or bet > max_bet:
                print(f"Please enter a valid bet amount from $1 to ${max_bet}.")
                continue
            current_money_bag = function_one(player_id)
            if bet > current_money_bag:
                print(f'You cannot bet more than your current funds: {current_money_bag}. Please try again')
                continue
            new_bag = current_money_bag - bet
            function_two(player_id, new_bag)
            return bet
        except ValueError:
            print("Invalid input. Please enter a numerical value.")
            
def table_bets(session, player_id, money_bag, get_player_money_bag, update_player_money_bag):

    if 1 <= money_bag <=250:
        max_bet = 20
        current_money_bag = get_player_money_bag(player_id)
        console.print(f"You currently have ${money_bag}.")
        user_input = prompt(f"Place a bet less than or equal to ${max_bet}.").strip()
        new_amount = current_money_bag - user_input
        update_player_money_bag(session, player_id, new_amount)
    
    elif 251 <= money_bag <=500:
        max_bet = 50
        current_money_bag = get_player_money_bag(player_id)
        console.print(f"You currently have ${money_bag}.")
        user_input = prompt(f"Place a bet less than or equal to ${max_bet}.").strip()
        new_amount = current_money_bag - user_input
        update_player_money_bag(session, player_id, new_amount)
        
    elif 501 <= money_bag <=1000:
        max_bet = 100
        current_money_bag = get_player_money_bag(player_id)
        console.print(f"You currently have ${money_bag}.")
        user_input = prompt(f"Place a bet less than or equal to ${max_bet}.").strip()
        new_amount = current_money_bag - user_input
        update_player_money_bag(session, player_id, new_amount)
        
    elif 1001 <= money_bag <=5000:
        max_bet = 250
        current_money_bag = get_player_money_bag(player_id)
        console.print(f"You currently have ${money_bag}.")
        user_input = prompt(f"Place a bet less than or equal to ${max_bet}.").strip()
        new_amount = current_money_bag - user_input
        update_player_money_bag(session, player_id, new_amount)
        
    elif 5001 <= money_bag <=10000:
        max_bet = 500
        current_money_bag = get_player_money_bag(player_id)
        console.print(f"You currently have ${money_bag}.")
        user_input = prompt(f"Place a bet less than or equal to ${max_bet}.").strip()
        new_amount = current_money_bag - user_input
        update_player_money_bag(session, player_id, new_amount)
        
    elif 10001 < money_bag:
        max_bet = 1000
        current_money_bag = get_player_money_bag(player_id)
        console.print(f"You currently have ${money_bag}.")
        user_input = prompt(f"Place a bet less than or equal to ${max_bet}.").strip()
        new_amount = current_money_bag - user_input
        update_player_money_bag(session, player_id, new_amount)
        
        
        
        
        
