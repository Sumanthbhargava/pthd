from otree.api import *
import json


doc = """
This is a one-shot "Prisoner's Dilemma". Two players are asked separately
whether they want to cooperate or defect. Their choices directly determine the
payoffs.
"""


class C(BaseConstants):
    NAME_IN_URL = 'cdg_intro'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1
    PAYOFF_A = cu(300)
    PAYOFF_B = cu(200)
    PAYOFF_C = cu(100)
    PAYOFF_D = cu(0)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass

def creating_session(subsession: Subsession):
    for i in range(0,len(subsession.get_players())):
        if i == subsession.session.config['number_of_bots']:
            break
        bot_player = subsession.get_players()[i]  # Example: Assigns the first player as the bot
        bot_player.participant.vars['is_bot'] = True  # Mark this player as a bot


# PAGES
class Introduction(Page):
    @staticmethod
    def get_timeout_seconds(player: Player): # Adding timeout for bot to proceed to next page automatically
        if player.participant.is_bot == True:
            return 10  # Set a 10-second timeout for the bot
        return 60 * 2  # Normal timeout for human players

page_sequence = [Introduction]
