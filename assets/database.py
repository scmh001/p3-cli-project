from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    
    def __repr__(self):
        return f"<Player(id={self.id}, name='{self.name}')>"

class GameSession(Base):
    __tablename__ = 'game_sessions'
    
    id = Column(Integer, primary_key=True) 
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    player_id = Column(Integer, ForeignKey('players.id'))
    dealer_hand_value = Column(Integer)
    player_hand_value = Column(Integer)
    outcome = Column(String)
    
    def __repr__(self):
        return f"<GameSession(id={self.id}, timestamp='{self.timestamp}', player_id={self.player_id}, dealer_hand_value={self.dealer_hand_value}, player_hand_value={self.player_hand_value}, outcome='{self.outcome}')>"
        
def init_db(engine):
    Base.metadata.create_all(bind=engine)

def get_db_engine(db_url):
    return create_engine(db_url)