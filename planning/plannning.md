
todo tracker
scheduler

note taker
quizzer (flashcard)
flashcard - game (right / wrong tracker (score))
card game - (cards and poker hands db)
card game - (blackjack)

inventory tracker
menu updater (restaurant)

card game - (blackjack)
* card draw
* 52 db entries (cards)
* randomize card draw
* shuffle deck
* reset deck
* user hand db
* dealer hand db
* dealer draw
* over 21 ends game
* ace = 1 or 11
* dealer must hit below value 16
* stand on value 17
* ask to play again
* betting

stretch
* multiple players
* counting player wins
* username input
* Special effect on winning(21)
* audio bytes to card draw, losing, shuffle

#user stories
> as a user i can
* "hit" "stand"
* place bet



python blackjack.py --play
|
`---> Enter player name
     |
     `---> Deck Shuffled
          |
          `---> Cards are dealt
               |
               |   `---> Displays cards dealt
               |       |
               |       `---> Calculate hand total
               |           |
               |           `---> Players chooses hit / stand
               |               |
               |               `---> Game Executed
               |                   |
               |                   `---> Game Recorded
               |
               `---> 
                     |
                     `---> Dealer's hand dealt and calculated
                          |
                          `---> Compare player and dealer hands
                               |
                               |   `---> Determine winner (player, dealer or push)
                               |       |
                               |       `---> Update player outcome/bet
                               |
                               `---> Offer player to play another hand
                                    |
                                    |   `---> [If yes, loop back to shuffling deck]
                                    |
                                    `---> [If no, exit game]