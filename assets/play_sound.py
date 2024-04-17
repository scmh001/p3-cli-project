import pygame

"""get_busy function returns 'true' if sound is still playing when checked. Clock().tick(10) defines an amount of time
to wait before checking if the sound has finished playing."""
def play_sound(file_path: str):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
        
def play_card_draw_sound():
    """Plays the sound effect for drawing a card."""
    play_sound("cardsounds/card-sounds-35956.wav")

def play_shuffle_sound():
    """Plays the sound effect for shuffling the deck."""
    play_sound("cardsounds/shuffle-cards-46455.wav")
    
def play_win_sound():
    """Plays a victory sound"""
    play_sound("cardsounds/success-1-6297.wav")
    
def play_loss_sound():
    """Plays game loss sound"""
    play_sound("cardsounds/game_loss.wav")

def coin_sound():
    """Plays a coin sound"""
    play_sound("cardsounds/coin_sound.wav")
    
def play_again_sound():
    """Plays sound when entering name"""
    play_sound("cardsounds/play_again.wav")
    
def play_title_music():
    """Plays music on title screen"""
    play_sound("cardsounds/game_music_loop.wav")
    
def play_start_sound():
    """Plays sound at game start"""
    play_sound("cardsounds/start_game_sound.wav")