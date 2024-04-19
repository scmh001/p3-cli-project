# CLI Blackjack

## Description
Blackjack CLI is a command-line interface application that lets you experience the thrill of the classic casino card game right from your terminal. Engage in a challenging game against a computerized dealer and test your strategy and luck.
The project incorporates sophisticated card counting logic, which the AI leverages to provide optimal decision-making assistance to players

## 🚀 Usage
To start type command below in user-terminal; type play; enter player name; begin.
>python blackjack.py

Follow the on-screen prompts to enter your **player** name and **play** the game. You can choose to **hit** or **stand** on your turn. The game will display the outcome (win, loss, or tie) after each round.
To view past game outcomes, enter **'view'** at the main menu. To quit the game, enter **'quit'**.
### OpenAI

>Note: Use your own openai API key by getting a free one [OpenAI](https://openai.com/) and paste it in .env file to use AI help features.

>Note: Create a .env file in assets directory and paste  **OPENAI_API_KEY=** with your key after = sign to us help features.

**DO NOT SHARE YOUR SECRET KEY -- DO NOT PUSH TO GITHUB WITH KEY ACTIVE**

Use openai version 0.27
>pip install openai==0.27


## ⚙️ Technologies / Libraries Include:
1. Python: The core language used for development.
2. Rich: Provides enhanced CLI formatting.
3. Prompt Toolkit: Facilitates interactive command-line prompts.
4. Click: Simplifies CLI creation.
5. SQLAlchemy: Manages database interactions.
6. Argparse: Adds helpful command-line options.
7. Pygame: Audio mixer usage.
8. OpenAI: Powerful AI text generation ( GPT-3.5 )
9. Typing: Type hints for Python


## 🎲 Deliverables: 
> (User Stories):
* Real-Time Decisions: Choose to "hit" or "stand" on your turn and watch as the game unfolds in real time.
* Player draw and Dealer draw
* Randomized card draw and deck shuffling
* Reset deck functionality
* Game End Conditions: The game automatically concludes if your card total exceeds 21.
* Ace Handling: Choose whether an Ace holds a value of 1 or 11, based on your strategy.
* Dealer Rules: Dealer hits below 16 and stands on 17 or above.
* Replayability: After each round, decide if you want to play again with just a simple command.
* Tracking player wins
* Username input
* Determine winner
* Integrate betting system


## 🌟 Stretch Deliverables: 
> (Future Enhancements):
* Implement multiplayer functionality (computer)
* AI implementation (help suggestions)
* Special effect on winning (21)
* Add special effects and audio for winning hands
* Support multiple decks
* Implement resume game feature (player money history)
* Visual representation of cards
* Enhance ASCII art card representations
* Migrate to SQLAlchemy for database management.
* Winning Hand Outcomes

## Database Schema
>Database Schema

The application uses a SQLAlchemy database ( blackjack.db) to store player information and game outcomes. 
The database contains two tables:
* players: Stores player_ID, name, money_bag
* game_sessions: Stores game outcomes with player_ID, dealer and player hand values, and outcome (win/loss/tie)

## 🗺️ Decision Tree
>Decision Tree

<img src="planning/decisiontree3.JPG" alt="decision-tree">

## 🗺️ Diagram
> Diagram of database including relationships, constraints, intended CRUD actions

<img src="planning/diagram6.JPG" alt="diagram">

## 🗺️ Trello Board
>The project tasks and progress were managed using a Trello board

<img src="planning/trello3.JPG" alt="trello"/>

## 🤝 Meet the Team

* Shukri Hussein 🔗[GitHub Profile Link](https://github.com/scmh001) 🔗 [LinkedIn Link](https://www.linkedin.com/in/shukrihussein/)
* Keenan Weise 🔗[GitHub Profile Link](https://github.com/kcweise) 🔗[LinkedIn Link](https://www.linkedin.com/in/keenan-weise/)
* Michael DiPasquale 🔗[GitHub Profile Link](https://github.com/mdipasqu13) 🔗[LinkedIn Link](https://www.linkedin.com/in/michael-dipasquale313/)

## 🙌 Acknowledgements
* The project was inspired by the classic game of Blackjack.
* Special thanks to the open-source community for their valuable libraries and resources.
