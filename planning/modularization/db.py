from sqlalchemy.orm import sessionmaker
from database import GameSession, Player, get_db_engine, init_db

def get_or_create_player(session, name: str) -> Player:
    player = session.query(Player).filter_by(name=name).first()
    if not player:
        player = Player(name=name)
        session.add(player)
        session.commit()
    return player

def get_player_money_bag(session, player_id: int) -> int:
    player = session.query(Player).filter_by(id=player_id).first()
    return player.money_bag if player else None

def update_player_money_bag(session, player_id: int, new_amount: int) -> None:
    player = session.query(Player).filter_by(id=player_id).first()
    if player:
        player.money_bag = new_amount
        session.commit()
    else:
        raise Exception("Player not found")

def record_game_session(
    session,
    player_id: int,
    dealer_hand,
    player_hand,
    outcome: str,
) -> None:
    game_session = GameSession(
        player_id=player_id,
        dealer_hand_value=dealer_hand.calculate_value(),
        player_hand_value=player_hand.calculate_value(),
        outcome=outcome,
    )
    session.add(game_session)
    session.commit()