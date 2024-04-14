#    _____ _      _____   ____  _            _    _            _    
  / ____| |    |_   _| |  _ \| |          | |  (_)          | |   
 | |    | |      | |   | |_) | | __ _  ___| | ___  __ _  ___| | __
 | |    | |      | |   |  _ <| |/ _` |/ __| |/ / |/ _` |/ __| |/ /
 | |____| |____ _| |_  | |_) | | (_| | (__|   <| | (_| | (__|   < 
  \_____|______|_____| |____/|_|\__,_|\___|_|\_\ |\__,_|\___|_|\_\
                                              _/ |                
                                             |__/           

## Description
Blackjack CLI is a command-line interface application that brings the excitement of the classic casino card game Blackjack to your terminal. Test your luck and skills by playing against the computer dealer in this interactive and entertaining game.

## Usage
To start type above command; enter player name; begin.
>python blackjack.py --play

Follow the on-screen prompts to enter your player name and play the game. You can choose to **hit** or **stand** on your turn. The game will display the outcome (win, loss, or tie) after each round.
To view past game outcomes, enter **'view'** at the main menu. To quit the game, enter **'quit'**.


## Technologies / Libraries Include:
1. Python
2. Rich library (for enhanced CLI formatting)
3. Prompt Toolkit (for interactive prompts)
4. Click (for command-line interface creation)
5. SQLAlchemy (for database management)
6. Argparse (help and usage messages)


## Deliverables: 
> (User Stories):
* Player draw
* Dealer draw
* Randomize card draw
* Shuffle deck
* Reset deck
* Over 21 ends game
* Ace = 1 or 11
* Dealer must hit below value 16
* Stand on value 17
* Ask to play again
* Tracking player wins (incomplete)
* Username input
* Determine winner
* Integrate betting system
* Fleshing out argparse commands

## Stretch Deliverables: 
> (Future Enhancements):
* Implement multiplayer functionality (computer)
* ai implementation (multiple players)
* Special effect on winning(21)
* Add special effects and audio for winning hands
* Support multiple decks
* Implement resume game feature
* Visual representation of cards
* Enhance ASCII art card representations
* Migrate to SQLAlchemy

## Database Schema
>Database Schema

The application uses a SQLAlchemy database ( blackjack.db) to store player information and game outcomes. The database contains two tables:
players: Stores player ID and name
game_sessions: Stores game outcomes with player ID, dealer and player hand values, and outcome (win/loss/tie)

## Decision Tree
>A decision tree of the flow of your CLI.  

<img src="planning/decisiontree2.JPG" alt="decision-tree">

## Diagram
> Diagram of database including relationships, constraints, intended CRUD actions

<img src="planning/diagram5.JPG" alt="diagram">

## Trello Board
>A kanban board showing how you will be dividing tasks among partners

<img src="planning/trello2.JPG" alt="trello"/>

## Collaborators

* Shukri Hussein 🔗[GitHub Profile Link](https://github.com/scmh001) 🔗 [LinkedIn Link](https://www.linkedin.com/in/shukrihussein/)
* Keenan Weise 🔗[GitHub Profile Link](https://github.com/kcweise) 🔗[LinkedIn Link](https://www.linkedin.com/in/keenan-weise/)
* Michael DiPasquale 🔗[GitHub Profile Link](https://github.com/mdipasqu13) 🔗[LinkedIn Link](https://www.linkedin.com/in/michael-dipasquale313/)

## Acknowledgements
* The project was inspired by the classic game of Blackjack.
* Special thanks to the open-source community for their valuable libraries and resources.