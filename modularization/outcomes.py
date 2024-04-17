from rich.console import Console
from rich.table import Table
from sqlalchemy.orm import Session

from database import GameSession, Player

console = Console()

def determine_outcome(player_hand_value: int, dealer_hand_value: int) -> str:
    if player_hand_value > 21:
        return "Loss"
    elif dealer_hand_value > 21:
        return "Win"
    elif player_hand_value > dealer_hand_value:
        return "Win"
    elif player_hand_value < dealer_hand_value:
        return "Loss"
    else:
        return "Tie"

def update_money_bag(session: Session, player_id: int, amount: int, outcome: str) -> None:
    player = session.query(Player).filter_by(id=player_id).first()
    if player:
        if outcome == "win":
            player.money_bag += amount
        elif outcome == "loss":
            player.money_bag -= amount
        session.commit()
    else:
        raise Exception("Player not found")

def view_game_outcomes(session: Session) -> None:
    query = (
        session.query(
            GameSession.player_id,
            Player.name,
            GameSession.dealer_hand_value,
            GameSession.player_hand_value,
            GameSession.outcome,
        )
        .join(Player)
    )

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
            game_session.outcome,
        )

    console.print(table)