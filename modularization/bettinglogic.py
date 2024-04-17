def place_bets(session, player_id, current_money, get_player_money_bag, update_player_money_bag):
    while True:
        try:
            bet = int(input(f"You have ${current_money}. How much would you like to bet? "))
            if bet > current_money:
                print("You don't have enough money to place that bet.")
            elif bet < 1:
                print("Bet must be at least $1.")
            else:
                new_amount = get_player_money_bag(session, player_id) - bet
                update_player_money_bag(session, player_id, new_amount)
                return bet
        except ValueError:
            print("Invalid input. Please enter a number.")

def table_bets(session, player_id, current_money, get_player_money_bag, update_player_money_bag):
    print(f"You have ${current_money}.")
    print("Betting options:")
    print("1. $10")
    print("2. $25")
    print("3. $50")
    print("4. $100")
    print("5. Custom amount")
    
    while True:
        choice = input("Enter your choice (1-5): ")
        if choice == "1":
            bet = 10
        elif choice == "2":
            bet = 25
        elif choice == "3":
            bet = 50
        elif choice == "4":
            bet = 100
        elif choice == "5":
            return place_bets(session, player_id, current_money, get_player_money_bag, update_player_money_bag)
        else:
            print("Invalid choice. Please try again.")
            continue
            
        if bet > current_money:
            print("You don't have enough money to place that bet.")
        else:
            new_amount = get_player_money_bag(session, player_id) - bet
            update_player_money_bag(session, player_id, new_amount)
            return bet