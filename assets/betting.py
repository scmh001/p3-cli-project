from prompt_toolkit import prompt

def place_bets(max_bet, player_id, 
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