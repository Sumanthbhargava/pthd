from otree.api import Currency as c, currency_range, expect, Bot
from . import *
import time

class PlayerBot(Bot):
    def play_round(self):
        if self.participant.id_in_session == 1:
            yield Decision, dict(cooperate=True)
            opponent= self.player.get_others_in_group()[0]
            opponent_records = json.loads(opponent.field_maybe_none('game_record')) if opponent.field_maybe_none('game_record') else []
            if opponent_records != []:
                latest_record= opponent_records[-1]
                print(latest_record)
                if latest_record['your_decision'] == "Cooperate":
                    yield Decision, dict(cooperate=True)
                else:
                    yield Decision, dict(cooperate=False)
            else: 
                print("No past opponent records")
        else:
            time.sleep(10)
            yield Decision, dict(cooperate=False)
            time.sleep(10)
            yield Decision, dict(cooperate=False)
            time.sleep(10)
        
        yield Results
        time.sleep(10)