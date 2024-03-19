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
    PLAYERS_PER_GROUP = 4 # for 1 bot
    BOT_LOGIC = 'cdu'
    intended_players_per_group = 6
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
    bot_records = models.LongStringField()
    temp_bot_records = models.LongStringField()
    n = models.IntegerField(initial = 0)

    def get_last_bot_details(self):
        group_last_round = self.in_round(self.round_number - 1)
        return json.loads(group_last_round.field_maybe_none('bot_records'))

    def update_n(self):
        if self.n == 0:
            self.n = C.intended_players_per_group - C.PLAYERS_PER_GROUP

    def get_filtered_bot_records(self):
        # Ensure n is updated correctly
        self.update_n()
        
        # Load all bot records into the temporary list if temp_bot_records is empty
        if not self.field_maybe_none('temp_bot_records'):
            self.temp_bot_records = json.dumps(self.get_last_bot_details()) if self.game =='1' else self.field_maybe_none('bot_records')
        all_bot_records = json.loads(self.field_maybe_none('temp_bot_records')) if self.field_maybe_none('temp_bot_records') else []
        print(all_bot_records)
        # Temporary list to store selected bot records
        selected_records = []

        if self.n > 0:
            # Calculate the indices of the records to be selected and removed
            indices_to_select = range(0, len(all_bot_records), self.n)

            # Select the records based on the calculated indices
            selected_records = [all_bot_records[i] for i in indices_to_select]
            print(selected_records)
            # Remove the selected records from all_bot_records
            # It's safer to remove items in reverse order to not mess up the indices
            for index in sorted(indices_to_select, reverse=True):
                all_bot_records.pop(index)
        
        # Update temp_bot_records with what's left after removing selected records
        self.temp_bot_records = json.dumps(all_bot_records)
        print('n=',self.n)
        self.n -= 1
        return selected_records


    def add_bot_record(self, opponent, self_payoff, opponent_payoff, bot_cooperate):
        if not self.field_maybe_none('bot_records'):
            if self.round_number>1:
                records = self.get_last_bot_details()
            else:
                records = []
        else:
            records = json.loads(self.field_maybe_none('bot_records'))
        # Add the new record
        record = {
            'round': self.round_number,
            'game': self.game,
            'opponent_id': opponent.unique_id,
            'your_id': -1,
            'opponent_decision': "A" if opponent.cooperate else "B",
            'your_decision': "A" if bot_cooperate else "B",
            'your_payoff': self_payoff,
            'opponent_payoff': opponent_payoff,
            'your_subgroup': -1,
            'opponent_subgroup': opponent.subgroup,
        }
        records.append(record)

        # Save the updated list
        self.bot_records = json.dumps(records)


    def assign_against_bot(self):
        all_players = self.get_players()
        num_bots = C.intended_players_per_group - C.PLAYERS_PER_GROUP
        players_to_assign_bot = random.sample(all_players, num_bots)
        for player in all_players:
            player.against_bot = player in players_to_assign_bot

    def assign_subgroups(self):
        all_players = self.get_players()

        # First, set the subgroup for players against bots to -1
        for player in all_players:
            if player.against_bot:
                player.subgroup = -1

        # Next, filter out players who are marked to play against bots and pair the rest
        players_not_against_bot = [p for p in all_players if not p.against_bot]

        random.shuffle(players_not_against_bot)

        # Assign subgroups for players not against bots
        for i, player in enumerate(players_not_against_bot):
            player.subgroup = (i // 2) + 1

class Player(BasePlayer):
    cooperate = models.BooleanField(
        choices=[[True, 'Cooperate'], [False, 'Defect']],
        doc="""This player's decision""",
        widget = widgets.RadioSelect,
    )
    unique_id = models.IntegerField() # Unique identifier of the player
    against_bot = models.BooleanField(initial=False)
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
        if self.against_bot == False:
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

        else:
            record = {
                'round': self.round_number,
                'game': self.group.game,
                'opponent_id': opponent['unique_id'],
                'your_id': self.unique_id,
                'opponent_decision': "A" if opponent['cooperate'] else "B",
                'your_decision': "A" if self.cooperate else "B",
                'your_payoff': self_payoff,
                'opponent_payoff': opponent_payoff,
                'your_subgroup': self.subgroup,
                'opponent_subgroup': opponent['subgroup'],
            }
        records.append(record)

        # Save the updated list
        self.game_record = json.dumps(records)
    
    def get_other_in_subgroup(self): # ** Finding the other players for payoff calculations, and updating records **
        players = self.get_others_in_group() # fetching all other players in group excluding current player
        for player in players:
            if player.field_maybe_none('subgroup') == self.field_maybe_none('subgroup'): #find the other player based on subgroup attribute
                return player
        return None


def creating_session(subsession: Subsession):
    for player in subsession.get_players():
        # Assign unique_id to all players
        player.set_unique_id()
        player.participant.vars['is_bot'] = False
   

# FUNCTIONS

def bot_logic(player: Player, logic):
    if logic == 'cdu':
        if player.group.game == '1':
            return True
        else:
            player_records = json.loads(player.field_maybe_none('game_record')) if player.field_maybe_none('game_record') else []
            if player_records != []:
                latest_record= player_records[-1]
                if latest_record['your_decision'] == "A":
                    your_decision = True # Cooperate if opponent has cooperated
                else:
                    your_decision =  False  # Defect if opponent has defected 
    else:
        your_decision =  random.choice([True, False]) 
    
    return your_decision

def update_bot_records(player: Player, bot_pay, opponent_pay, bot_cooperate):
    player.group.add_bot_record(player, bot_pay, opponent_pay, bot_cooperate)

def set_payoffs_and_records(group: Group):
    for p in group.get_players():
        bot_pay, bot_cooperate = set_payoff(p)
        if p.against_bot == False:
            opponent = other_player(p)
            update_game_record(p, p.game_pay, opponent.game_pay)
        else:
            update_game_record(p, p.game_pay, bot_pay)
            update_bot_records(p,bot_pay,p.game_pay, bot_cooperate)

    for p in group.get_players():
        add_payoff(p)

def update_game_record(player: Player, self_payoff, opponent_payoff):
    if player.against_bot == False:
        opponent = other_player(player)
        player.add_game_record(opponent, self_payoff, opponent_payoff)
    else:
        opponent = dict(
            unique_id = -1,
            cooperate = bot_logic(player, C.BOT_LOGIC),
            subgroup = -1
        )
        player.add_game_record(opponent, self_payoff, opponent_payoff)

def other_player(player: Player):
    return player.get_other_in_subgroup()

def set_payoff(player: Player):
    game_12 = player.group.game
    if game_12 == '1':
        payoff_matrix = C.PAYOFF_MATRIX_1
    elif game_12 == '2':
        payoff_matrix = C.PAYOFF_MATRIX_2
    else:
        raise ValueError(f"Invalid game type: {game_12}")
    if player.against_bot == False: 
        opponent = other_player(player)
        player.game_pay = float(payoff_matrix[(player.cooperate, opponent.cooperate)])
        return None , None
    else:
        bot_cooperate = bot_logic(player, C.BOT_LOGIC)
        player.game_pay = float(payoff_matrix[(player.cooperate, bot_cooperate)])
        return float(payoff_matrix[(bot_cooperate, player.cooperate)]) , bot_cooperate

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
        
def get_bot_details(player: Player):
    group = player.group
    
    # Call the method to get filtered bot records
    selected_bot_records = group.get_filtered_bot_records()
    
    # Logic to return these records or handle them as needed
    return selected_bot_records

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
        current_round = player.round_number
        if player.against_bot == False:
            opponent = other_player(player)
            opponent_records = get_player_details(opponent)
            opponent_decision = opponent.field_maybe_none('cooperate')
        else:
            opponent_records = [] if player.group.game == '1' and player.round_number == 1 else get_bot_details(player)
            opponent_decision = None
        
        filtered_records = get_filtered_records(player, opponent_records, current_round)
        opponent_last_choice = get_last_choice(opponent_records)   
        self_records = get_player_details(player)
        last_record = self_records[-1] if self_records != [] else None
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
            #same_choice = player.field_maybe_none('cooperate') == opponent.field_maybe_none('cooperate'),
            my_decision = player.field_maybe_none('cooperate'),
            opponent_decision = opponent_decision,
            condition = condition,
            opponent_last_choice = opponent_last_choice,
            directinteraction = directinteraction,
            subgroup = player.field_maybe_none('subgroup'),
        )
    @staticmethod
    def before_next_page(player: Player, timeout_happened): #Bot logic
        if player.participant.vars.get('is_bot', False) and timeout_happened: # if bot implement bot logic
            if player.unique_id == 1:
                opponent= player.get_other_in_subgroup()
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
        last_record = self_records[-1] if self_records != [] else None
        current_round = player.round_number
        if player.against_bot == False:
            opponent = other_player(player)
            opponent_records = get_player_details(opponent)
            opponent_last_choice = get_last_choice(opponent_records)
            filtered_records = get_filtered_records(player, opponent_records, current_round)
            opponent_decision = opponent.field_maybe_none('cooperate')
        else:
            opponent_records = None
            filtered_records = None
            opponent_last_choice = None
            opponent_decision = None
        final_payoff = player.participant.payoff
        final_amount = player.participant.payoff_plus_participation_fee()
        return dict(
            #same_choice=player.cooperate == opponent.cooperate,
            my_decision=player.field_display('cooperate'),
            opponent_decision=opponent_decision,
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
        current_round = player.round_number
        if player.against_bot == False:
            opponent = other_player(player)
            opponent_records = get_player_details(opponent)
            opponent_decision = opponent.field_maybe_none('cooperate')
        else:
            opponent_records = None
            filtered_records = None
            opponent_last_choice = None
            opponent_decision = None
        self_records = json.loads(player.field_maybe_none('game_record')) if player.field_maybe_none('game_record') else []
        last_record = self_records[-1] if self_records != [] else None
        return dict(
            #same_choice = player.cooperate == opponent.cooperate,
            my_decision = player.field_display('cooperate'),
            opponent_decision = opponent_decision,
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
            group.assign_against_bot()
            group.assign_subgroups()
            print("Players shuffled and Subgroups formed successfully!!")
            players = group.get_players()
            print(f"ROUND: {group.round_number} \n GAME: {group.game}")
            for player in players:
                print(f"Player ID: {player.unique_id}, Sub group: {player.subgroup}, AGAINST BOT: {player.against_bot}")



class GameGroupsPage(WaitPage):
    group_by_arrival_time = True

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1
    
    @staticmethod
    def after_all_players_arrive(group: Group):
        group.assign_against_bot()
        group.assign_subgroups()
        print("Players shuffled and Subgroups formed successfully!!")
        players = group.get_players()
        print(f"ROUND: {group.round_number} \n GAME: {group.game}")
        for player in players:
            print(f"Player ID: {player.unique_id}, Sub group: {player.subgroup}, AGAINST BOT: {player.against_bot}")


class GroupsPage(WaitPage):

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number != 1
    
    @staticmethod
    def after_all_players_arrive(group: Group):
        group.assign_against_bot()
        group.assign_subgroups()
        print("Players shuffled and Subgroups formed successfully!!")
        players = group.get_players()
        print(f"ROUND: {group.round_number} \n GAME: {group.game}")
        for player in players:
            print(f"Player ID: {player.unique_id}, Sub group: {player.subgroup}, AGAINST BOT: {player.against_bot}")


page_sequence = [GameGroupsPage, GroupsPage, Decision, ResultsWaitPage, GroupsShufflePage, Decision, ResultsWaitPage, RoundResults, Results]
