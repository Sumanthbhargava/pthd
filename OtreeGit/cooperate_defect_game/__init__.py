from otree.api import *
import json
import random

doc = """
This is a one-shot "Prisoner's Dilemma". Two players are asked separately
whether they want to cooperate or defect. Their choices directly determine the
payoffs.
"""


class C(BaseConstants):
    NAME_IN_URL = 'coop_defect_game'
    PLAYERS_PER_GROUP = 6 # Can not have groups of 2, need fixeed group of six to shuffle pairs within 
    NUM_ROUNDS = 3
    L = 2 # Depricated, to be removed
    CONDITION = 4 # Depricated, to be removed
    PAYOFF_A = cu(300)
    PAYOFF_B = cu(200)
    PAYOFF_C = cu(100)
    PAYOFF_D = cu(0)
    PAYOFF_MATRIX_1 = {
        (False, True): cu(5),  
        (True, True): cu(3),
        (False, False): cu(1),
        (True, False): cu(0),
    }
    PAYOFF_MATRIX_2 = {
        (False, True): cu(5), 
        (True, True): cu(3),
        (False, False): cu(0),
        (True, False): cu(1),
    }

class Subsession(BaseSubsession):
    pass #Contains all players in the subessio, so methods should be moved to group

class Group(BaseGroup):
    #define a game variable(initalized as A) which toggles between Game A and Game B. Assuming it gets set to A at the beginning of a round, and in the 'GroupsShufflePage' the game is toggled to game 'B' as it concludes game A.
    game=models.StringField(initial='1')

    def assign_subgroups(self): # Otree has no sub-group functionality, since we can't put players into subgroups, we make a subgroup attribute.
        players = self.get_players() # fetching the list players in the group

        random.shuffle(players) # shuffling the order of the players in the list

        for i, player in enumerate(players): #enumerate gives index i and the element at the index 'player'
            #assigning each player to a subgroup based on their order in the randomized list
            player.subgroup = (i//2) + 1  # first two players first pair, next two second pair, so on

class Player(BasePlayer):
    cooperate = models.BooleanField(
        choices=[[True, 'Cooperate'], [False, 'Defect']],
        doc="""This player's decision""",
        widget = widgets.RadioSelect,
    )
    unique_id = models.IntegerField() # Unique identifier of the player
    
    subgroup = models.IntegerField() # subgroup field which identifies the modified subgroups

    game_pay = models.FloatField(initial=0.0)
    #variable for recording game events
    game_record = models.LongStringField()

    def set_unique_id(self):
        self.unique_id = self.participant.id_in_session

    #method to add to game_record during the game
    def add_game_record(self, opponent, self_payoff, opponent_payoff):
        # Initialize the list if it's empty
        if not self.field_maybe_none('game_record'):
            if self.round_number>1:
                records = get_last_details(self)
            else:
                records = []
        else:
            records = json.loads(self.field_maybe_none('game_record'))
        
        # Add the new record
        record = {
            'round': self.round_number,
            'game': self.group.game,
            'opponent_id': opponent.unique_id,
            'your_id': self.unique_id,
            'opponent_decision': "A" if opponent.cooperate else "B",
            'your_decision': "A" if self.cooperate else "B",
            'your_payoff': self_payoff,
            'opponent_payoff': opponent_payoff,
            'your_subgroup': self.subgroup,
            'opponent_subgroup': opponent.subgroup,
        }
        records.append(record)

        # Save the updated list
        self.game_record = json.dumps(records)
    
    def get_other_in_subgroup(self): # ** Finding the other players for payoff calculations, and updating records **
        players = self.get_other_in_group() # fetching all other players in group excluding current player
        for player in players:
            if player.field_maybe_none('subgroup') == self.field_maybe_none('subgroup'): #find the other player based on subgroup attribute
                return player
        return None


def creating_session(subsession: Subsession): # unique id and botassignment the only 2 things which should happen in while creating session
    for player in subsession.get_players():
        player.set_unique_id()

    for i in range(0,len(subsession.get_players())):
        if i == subsession.session.config['number_of_bots']:
            break
        bot_player = subsession.get_players()[i]  # Example: Assigns the first player as the bot
        bot_player.participant.vars['is_bot'] = True  # Mark this player as a bot

# FUNCTIONS

def set_payoffs_and_records_for_all_groups(subsession: Subsession): #decprecated need to be removed as only one group will be there
    for group in subsession.get_groups():
        set_payoffs_and_records(group)

def set_payoffs_and_records(group: Group):
    for p in group.get_players():
        set_payoff(p)

    for p in group.get_players():
        opponent = other_player(p)
        update_game_record(p, p.game_pay, opponent.game_pay)

    for p in group.get_players():
        add_payoff(p)

def update_game_record(player: Player, self_payoff, opponent_payoff):
    opponent = other_player(player)
    player.add_game_record(opponent, self_payoff, opponent_payoff)

def other_player(player: Player):
    return player.get_others_in_group()[0]

def set_payoff(player: Player):
    game_12 = player.group.game
    if game_12 == '1':
        payoff_matrix = C.PAYOFF_MATRIX_1
    elif game_12 == '2':
        payoff_matrix = C.PAYOFF_MATRIX_2
    else:
        raise ValueError(f"Invalid game type: {game_12}")
    opponent = other_player(player)
    player.game_pay = float(payoff_matrix[(player.cooperate, opponent.cooperate)])

def get_last_details(player: Player):
    player_last_round = player.in_round(player.round_number-1)
    return json.loads(player_last_round.field_maybe_none('game_record'))

def add_payoff(player: Player):
    player.payoff = player.payoff + cu(player.game_pay)

def get_payoff_matrix(player: Player):
    game_12 = player.group.game
    if game_12 == '1':
        payoff_matrix = C.PAYOFF_MATRIX_1
    elif game_12 == '2':
        payoff_matrix = C.PAYOFF_MATRIX_2
    else:
        raise ValueError(f"Invalid game type: {game_12}")

    
    return {
        'cooperate_cooperate': payoff_matrix[(True, True)],
        'cooperate_defect': payoff_matrix[(True, False)],
        'defect_cooperate': payoff_matrix[(False, True)],
        'defect_defect': payoff_matrix[(False, False)],
    }

def get_player_details(player: Player):
    records = json.loads(player.field_maybe_none('game_record')) if player.field_maybe_none('game_record') else []
    if player.round_number > 1:
        if records == []:
            records = get_last_details(player)
    return records
        
def get_filtered_records(player: Player, records, current_round):
    condition = player.session.config['past_records_display_condition_1_to_4']
    l_rounds = player.session.config['no_of_past_rounds_to_be_displayed']
    l= l_rounds if l_rounds < current_round else current_round
    if condition == 1 or condition == 2:
        filtered_records = [record for record in records if record['game'] == 'A']
        return filtered_records[-l:]
    elif condition == 3 or condition == 4:
        filtered_records = get_restructured_data(records)
        return filtered_records[-l:]
    else:
        return records

def get_restructured_data(records):
    # Initialize a new list to hold the restructured records
    restructured_records = []

    # Assuming each round has both a game A and a game B entry
    rounds = set(record['round'] for record in records)

    for round in rounds:
        record_a = next((r for r in records if r['round'] == round and r['game'] == '1'), None)
        record_b = next((r for r in records if r['round'] == round and r['game'] == '2'), None)

        restructured_record = {
            "round": round,
            "opponents_decision_in_game_A": record_a['your_decision'] if record_a else None,
            "opponents_opponent_decision_in_game_A": record_a['opponent_decision'] if record_a else None,
            "opponents_decision_in_game_B": record_b['your_decision'] if record_b else None,
            "opponents_opponent_decision_in_game_B": record_b['opponent_decision'] if record_b else None,
        }
        
        restructured_records.append(restructured_record)

    return restructured_records

def get_last_choice(records):
    last_choice = records[-1]['your_decision'] if records else None
    if last_choice == 'A':
        return 'A'
    elif last_choice == 'B':
        return 'B'
    else:
        return None

# PAGES
class Decision(Page):
    form_model = 'player'
    form_fields = ['cooperate']

    @staticmethod
    def get_timeout_seconds(player: Player): # Adding timeout for bot to proceed to next page automatically
        if player.participant.is_bot == True:
            return 10  # Set a 10-second timeout for the bot
        return None # Normal timeout for human players

    @staticmethod
    def vars_for_template(player: Player):
        is_bot = player.participant.vars.get('is_bot', False) # Sent to HTML to display a different decision page for bot
        payoffs = get_payoff_matrix(player)
        opponent = other_player(player)
        self_records = get_player_details(player)
        opponent_records = get_player_details(opponent)
        opponent_last_choice = get_last_choice(opponent_records)
        last_record = self_records[-1] if self_records != [] else None
        current_round = player.round_number
        filtered_records = get_filtered_records(player, opponent_records, current_round)
        directinteraction = player.session.config['directinteraction']
        condition = player.session.config['past_records_display_condition_1_to_4']
        return dict(
            is_bot=is_bot,
            payoffs=payoffs,
            opponent_records = opponent_records,
            filtered_records = filtered_records,
            last_record = last_record,
            game_12 = player.group.game,
            current_round = current_round,
            same_choice = player.field_maybe_none('cooperate') == opponent.field_maybe_none('cooperate'),
            my_decision = player.field_maybe_none('cooperate'),
            opponent_decision = opponent.field_maybe_none('cooperate'),
            condition = condition,
            opponent_last_choice = opponent_last_choice,
            directinteraction = directinteraction,
            subgroup = player.field_maybe_none('subgroup'),
        )
    @staticmethod
    def before_next_page(player: Player, timeout_happened): #Bot logic
        if player.participant.vars.get('is_bot', False) and timeout_happened: # if bot implement bot logic
            if player.unique_id == 1:
                opponent= player.get_others_in_group()[0]
                opponent_records = json.loads(opponent.field_maybe_none('game_record')) if opponent.field_maybe_none('game_record') else []
                if opponent_records != []:
                    latest_record= opponent_records[-1]
                    if latest_record['your_decision'] == "A":
                        player.cooperate = True  # Cooperate if opponent has cooperated
                    else:
                        player.cooperate = False  # Defect if opponent has defected 
                else: 
                    player.cooperate = True  # Cooperate in game A
            else:
                player.cooperate = random.choice([True, False]) 
                

class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs_and_records

class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def get_timeout_seconds(player: Player): # Adding timeout for bot to proceed to next page automatically
        if player.participant.vars.get('is_bot', False):
            return 30  # Set a 10-second timeout for the bot
        return None  # Normal timeout for human players
    
    @staticmethod
    def vars_for_template(player: Player,):
        opponent = other_player(player)
        self_records = get_player_details(player)
        opponent_records = get_player_details(opponent)
        opponent_last_choice = get_last_choice(opponent_records)
        last_record = self_records[-1] if self_records != [] else None
        current_round = player.round_number
        final_payoff = player.participant.payoff
        final_amount = player.participant.payoff_plus_participation_fee()
        return dict(
            same_choice=player.cooperate == opponent.cooperate,
            my_decision=player.field_display('cooperate'),
            opponent_decision=opponent.field_display('cooperate'),
            self_records=None,
            current_round = current_round,
            last_record= last_record,
            final_payoff = final_payoff,
            final_amount = final_amount,
        )

class RoundResults(Page):
    @staticmethod
    def get_timeout_seconds(player: Player): # Adding timeout for bot to proceed to next page automatically
        if player.participant.vars.get('is_bot', False):
            return 20  # Set a 10-second timeout for the bot
        return 60  # Normal timeout for human players
    
    @staticmethod
    def vars_for_template(player: Player,):
        opponent = other_player(player)
        self_records = json.loads(player.field_maybe_none('game_record')) if player.field_maybe_none('game_record') else []
        last_record = self_records[-1] if self_records != [] else None
        current_round = player.round_number
        return dict(
            same_choice = player.cooperate == opponent.cooperate,
            my_decision = player.field_display('cooperate'),
            opponent_decision = opponent.field_display('cooperate'),
            self_records = None,
            current_round = current_round,
            last_record = last_record,
        )

class GroupsShufflePage(WaitPage):
    
    @staticmethod
    def after_all_players_arrive(group: Group):
        #Get direct interaction from config
        directinteraction = group.subsession.session.config['directinteraction']
        if group.game == '1':
            group.game = '2'
        else:
            pass

        if directinteraction == 1:
            pass
        else:
            group.assign_subgroups()
            print("Players shuffled and Subgroups formed successfully!!")
            players = group.get_players()
            print(f"ROUND: {group.round_number} \n GAME: {group.game}")
            for player in players:
                print(f"Player ID: {player.unique_id}, Sub group: {player.subgroup}")


class GameGroupsPage(WaitPage):
    group_by_arrival_time = True

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1
    
    def after_all_players_arrive(group: Group):
        group.assign_subgroups()
        print("Players shuffled and Subgroups formed successfully!!")
        players = group.get_players()
        print(f"ROUND: {group.round_number} \n GAME: {group.game}")
        for player in players:
            print(f"Player ID: {player.unique_id}, Sub group: {player.subgroup}")


class GroupsPage(WaitPage):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number != 1
    
    def after_all_players_arrive(group: Group):
        group.assign_subgroups()
        print("Players shuffled and Subgroups formed successfully!!")
        players = group.get_players()
        print(f"ROUND: {group.round_number} \n GAME: {group.game}")
        for player in players:
            print(f"Player ID: {player.unique_id}, Sub group: {player.subgroup}")
        

page_sequence = [GameGroupsPage, GroupsPage, Decision, ResultsWaitPage, GroupsShufflePage, Decision, ResultsWaitPage, RoundResults, Results]
