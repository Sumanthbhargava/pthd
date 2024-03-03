from otree.api import Bot
from otree.api import *
from otree.api import BaseConstants,widgets
import time
confCheck = True

class Page(Page):
    subsession: BaseSubsession
    group: BaseGroup
    player: BasePlayer

class WaitPage(WaitPage):
    subsession: BaseSubsession
    group: BaseGroup
    player: BasePlayer

class MyBot(Bot):
    subsession = BaseSubsession
    group = BaseGroup
    player = BasePlayer

class Constants(BaseConstants):
    name_in_url = 'Temperature'
    players_per_group = 6
    num_rounds = 25
    num_of_rounds = 3
    not_num_rounds = 50
    players_in_subgroup = 2

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class PlayerBot(Bot):
    def play_round(self):
        pass

class Player(BasePlayer):
    isCheck = models.BooleanField()
    wait_page_arrival = models.FloatField()

class Consent(Page):
    def is_displayed(self):
        return self.round_number == 1

class Instruction(Page):
    def is_displayed(self):
        return self.round_number == 1

    @staticmethod
    def get_timeout_seconds(player: Player): # Adding timeout for bot to proceed to next page automatically
        if player.participant.is_bot == True:
            player.isCheck = True
            return 10  # Set a 10-second timeout for the bot
        return 60 * 15 # Normal timeout for human players


    @staticmethod
    def vars_for_template(player: Player):
        directinteraction = player.subsession.session.config['directinteraction']
        l = player.subsession.session.config['no_of_past_rounds_to_be_displayed']
        condition = player.subsession.session.config['past_records_display_condition_1_to_4']
        return dict(
            round=player.session.config["num_rounds"],
            not_num_rounds = Constants.not_num_rounds, 
            confCheck=confCheck, 
            directinteraction = directinteraction, 
            no_of_participants = Constants.players_per_group,
            no_of_rounds = Constants.num_of_rounds,
            l = l,
            condition = condition,
            )

    @staticmethod
    def live_method(player,data):
        if data == 0:
            player.isCheck = False
        else:
            player.isCheck = True

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant

        participant.wait_page_arrival = time.time()  # record time before the wait page to be able to initialize timeout
        player.wait_page_arrival = participant.wait_page_arrival

        # print("+++ APPS!", player.session.config["app_sequence"])

        if "waitapp" not in player.session.config:
            participant.wait_page_arrival_game = time.time()
            print(participant.wait_page_arrival_game)

class ComprehensionFail(Page):
    def is_displayed(self):
        if self.round_number == 1:
            return self.isCheck == False
        else:
            return False

class Comprehension(Page):
    form_model = 'player'

    def is_displayed(player: Player):
        return player.round_number == 1

    def vars_for_template(player: Player):
            return dict(
                num_rounds = player.session.config["num_rounds"],
                not_num_rounds = Constants.not_num_rounds,
                confCheck=confCheck
        )

    @staticmethod
    def live_method(player,data):
        if data == 0:
            print("here")
            player.isCheck = False
        else:
            player.isCheck = True

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant

        participant.wait_page_arrival = time.time()  # record time before the wait page to be able to initialize timeout
        player.wait_page_arrival = participant.wait_page_arrival

        # print("+++ APPS!", player.session.config["app_sequence"])

        if "waitapp" not in player.session.config:
            participant.wait_page_arrival_game = time.time()
            print(participant.wait_page_arrival_game)


class ComprehensionPassed(Page):
    def vars_for_template(player: Player):
        return dict(wait_bonus_total=10,
                    wait_bonus_10sec=10,
                    wait_time_minutes=10,
                    participation_fee=10)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        participant = player.participant

        participant.wait_page_arrival = time.time()  # record time before the wait page to be able to initialize timeout
        player.wait_page_arrival = participant.wait_page_arrival

        # print("+++ APPS!", player.session.config["app_sequence"])

        if "waitapp" not in player.session.config:
            participant.wait_page_arrival_game = time.time()
            print(participant.wait_page_arrival_game)

# Consent, Instruction, Comprehension, ComprehensionFail
page_sequence = [Instruction, ComprehensionFail]