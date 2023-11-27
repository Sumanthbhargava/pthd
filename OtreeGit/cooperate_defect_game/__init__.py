from otree.api import *
import json


doc = """
This is a one-shot "Prisoner's Dilemma". Two players are asked separately
whether they want to cooperate or defect. Their choices directly determine the
payoffs.
"""


class C(BaseConstants):
    NAME_IN_URL = 'prisoner'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 3
    PAYOFF_A = cu(300)
    PAYOFF_B = cu(200)
    PAYOFF_C = cu(100)
    PAYOFF_D = cu(0)


class Subsession(BaseSubsession):
    #define a game variable(initalized as A) which toggles between Game A and Game B. Assuming it gets set to A at the beginning of a round, and in the 'GroupsShufflePage' the game is toggled to game 'B' as it concludes game A.
    game=models.StringField(initial='A')


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    cooperate = models.BooleanField(
        choices=[[True, 'Cooperate'], [False, 'Defect']],
        doc="""This player's decision""",
        widget=widgets.RadioSelect,
    )
    unique_id = models.IntegerField()

    #variable for recording game events
    opponent_record = models.LongStringField()

    def set_unique_id(self):
        self.unique_id = self.participant.id_in_session

    #method to add to opponent_record during the game
    def add_opponent_record(self, opponent):
        # Initialize the list if it's empty
        if not self.field_maybe_none('opponent_record'):
            records = []
        else:
            records = json.loads(self.field_maybe_none('opponent_record'))
        
        # Add the new record
        record = {
            'round': opponent.round_number,
            'game': 'A/B',
            'opponent_id': opponent.unique_id,
            'your_id': self.unique_id,
            'opponent_decision': opponent.cooperate,
            'your_decision': self.cooperate
        }
        records.append(record)

        # Save the updated list
        self.opponent_record = json.dumps(records)

def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        player.set_unique_id()
    
    # Randomly pairs 6 players into 3 pairs before game A
    subsession.group_randomly()

    """if subsession.game == 'C':
        subsession.game = 'A'
    elif subsession.game == 'A':
        subsession.game = 'B'
"""
# FUNCTIONS
def set_payoffs(group: Group):
    for p in group.get_players():
        set_payoff(p)


def other_player(player: Player):
    return player.get_others_in_group()[0]


def set_payoff(player: Player):
    payoff_matrix = {
        (False, True): C.PAYOFF_A,
        (True, True): C.PAYOFF_B,
        (False, False): C.PAYOFF_C,
        (True, False): C.PAYOFF_D,
    }
    other = other_player(player)
    player.payoff = payoff_matrix[(player.cooperate, other.cooperate)]



# PAGES
class Introduction(Page):
    timeout_seconds = 100


class Decision(Page):
    form_model = 'player'
    form_fields = ['cooperate']


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        opponent = other_player(player)
        player.add_opponent_record(opponent)
        opponent_records = json.loads(player.field_maybe_none('opponent_record')) if player.field_maybe_none('opponent_record') else []
        return dict(
            opponent=opponent_data,
            same_choice=player.cooperate == opponent.cooperate,
            my_decision=player.field_display('cooperate'),
            opponent_decision=opponent.field_display('cooperate'),
            opponent_records=opponent_records,
        )


class GroupsShufflePage(WaitPage):
    #Wait for all 6 players to be done with game A
    wait_for_all_groups = True 

    @staticmethod
    def after_all_players_arrive(subsession):
        #Shuffle players into new random pairs before they enter game B
        subsession.group_randomly()

        if subsession.game == 'A':
            subsession.game = 'B'
        else:
            pass

page_sequence = [Introduction, Decision, ResultsWaitPage, Results, GroupsShufflePage, Decision, ResultsWaitPage, Results]
