from otree.api import Currency as c, currency_range, expect, Bot
from . import *
import time
import random
class PlayerBot(Bot):
    def play_round(self):        
        time.sleep(10)
        yield Decision, dict(cooperate=random.choice([True, False]))
        time.sleep(10)
        yield Decision, dict(cooperate=random.choice([True, False]))
        time.sleep(10)
        yield Results
        time.sleep(10)