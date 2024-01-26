from otree.api import Currency as c, currency_range, expect, Bot
from . import *
import time
import random
class PlayerBot(Bot):
    def play_round(self):
        if self.participant.id_in_session == 1:
            pass
        else:
            time.sleep(10)
            yield Decision, dict(cooperate=random.choice(True, False))
            time.sleep(10)
            yield Decision, dict(cooperate=random.choice(True, False))
            time.sleep(10)
            yield Results
            time.sleep(10)

        """if self.participant.id_in_session == 1:  # Assign bot behavior to player 1
            yield Decision, dict(cooperate= True)
            yield Decision, dict(cooperate= True)
            yield Results"""