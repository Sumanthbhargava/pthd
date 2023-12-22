from otree.api import *
import json


doc = """
This is a one-shot "Prisoner's Dilemma". Two players are asked separately
whether they want to cooperate or defect. Their choices directly determine the
payoffs.
"""


class C(BaseConstants):
    NAME_IN_URL = 'coop_defect_game'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 3
    PAYOFF_A = cu(300)
    PAYOFF_B = cu(200)
    PAYOFF_C = cu(100)
    PAYOFF_D = cu(0)
    PAYOFF_MATRIX_A = {
        (False, True): cu(300),  
        (True, True): cu(200),
        (False, False): cu(100),
        (True, False): cu(0),
    }
    PAYOFF_MATRIX_B = {
        (False, True): cu(150), 
        (True, True): cu(100),
        (False, False): cu(50),
        (True, False): cu(0),
    }

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
    game_record = models.LongStringField()

    def set_unique_id(self):
        self.unique_id = self.participant.id_in_session

    #method to add to game_record during the game
    def add_game_record(self, opponent):
        # Initialize the list if it's empty
        if not self.field_maybe_none('game_record'):
            records = []
        else:
            records = json.loads(self.field_maybe_none('game_record'))
        
        # Add the new record
        record = {
            'round': opponent.round_number,
            'game': opponent.subsession.game,
            'opponent_id': opponent.unique_id,
            'your_id': self.unique_id,
            'opponent_decision': "Cooperate" if opponent.field_maybe_none('cooperate') == True else "Defect",
            'your_decision': "Cooperate" if self.field_maybe_none('cooperate') == True else "Defect"
        }
        records.append(record)

        # Save the updated list
        self.game_record = json.dumps(records)

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
def set_payoffs_and_records(group: Group):
    for p in group.get_players():
        set_payoff(p)
        update_game_record(p)

def update_game_record(player: Player):
    opponent = other_player(player)
    player.add_game_record(opponent)

def other_player(player: Player):
    return player.get_others_in_group()[0]


def set_payoff(player: Player):
    game_AB = player.subsession.game
    if game_AB == 'A':
        payoff_matrix = C.PAYOFF_MATRIX_A
    elif game_AB == 'B':
        payoff_matrix = C.PAYOFF_MATRIX_B
    else:
        raise ValueError(f"Invalid game type: {game_AB}")
    opponent = other_player(player)
    player.payoff = payoff_matrix[(player.cooperate, opponent.cooperate)]



# PAGES
class Introduction(Page):
    timeout_seconds = 100


class Decision(Page):
    form_model = 'player'
    form_fields = ['cooperate']
    @staticmethod
    def vars_for_template(player: Player):
        game_AB= player.subsession.game
        if game_AB == 'A':
            payoff_matrix = C.PAYOFF_MATRIX_A
        elif game_AB == 'B':
            payoff_matrix = C.PAYOFF_MATRIX_B
        else:
            raise ValueError(f"Invalid game type: {game_AB}")

        
        payoffs = {
            'cooperate_cooperate': payoff_matrix[(True, True)],
            'cooperate_defect': payoff_matrix[(True, False)],
            'defect_cooperate': payoff_matrix[(False, True)],
            'defect_defect': payoff_matrix[(False, False)],
        }
        opponent = other_player(player)
        opponent_records = json.loads(opponent.field_maybe_none('game_record')) if opponent.field_maybe_none('game_record') else []
        self_records = json.loads(player.field_maybe_none('game_record')) if player.field_maybe_none('game_record') else []
        last_record = self_records[-1] if self_records else None
        current_round = player.round_number
        return dict(
            payoffs=payoffs,
            opponent_records= opponent_records,
            last_record= last_record,
            game_AB = game_AB,
            current_round = current_round,
            same_choice=player.field_maybe_none('cooperate') == opponent.field_maybe_none('cooperate'),
            my_decision=player.field_maybe_none('cooperate'),
            opponent_decision=opponent.field_maybe_none('cooperate'),
        )


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs_and_records


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        opponent = other_player(player)
        self_records = json.loads(player.field_maybe_none('game_record')) if player.field_maybe_none('game_record') else []
        current_round = player.round_number
        return dict(
            same_choice=player.cooperate == opponent.cooperate,
            my_decision=player.field_display('cooperate'),
            opponent_decision=opponent.field_display('cooperate'),
            self_records=self_records,
            current_round = current_round,
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

page_sequence = [Decision, ResultsWaitPage, GroupsShufflePage, Decision,ResultsWaitPage, Results]
