from otree.api import Bot
from otree.api import *
from otree.api import BaseConstants,widgets
import random

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
    name_in_url = 'Gateway'
    players_per_group = 4
    num_rounds = 25
    not_num_rounds = 50

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class PlayerBot(Bot):
    def play_round(self):
        pass

class Player(BasePlayer):
    isCheck = models.BooleanField()
    captcha1 = models.BooleanField(widget=widgets.CheckboxInput, blank=True)
    captcha2 = models.BooleanField(widget=widgets.CheckboxInput, blank=True)
    captcha3 = models.BooleanField(widget=widgets.CheckboxInput, blank=True)
    captcha4 = models.BooleanField(widget=widgets.CheckboxInput, blank=True)
    captcha5 = models.BooleanField(widget=widgets.CheckboxInput, blank=True)
    captcha6 = models.BooleanField(widget=widgets.CheckboxInput, blank=True)
    captcha7 = models.BooleanField(widget=widgets.CheckboxInput, blank=True)
    captcha8 = models.BooleanField(widget=widgets.CheckboxInput, blank=True)
    captcha_score = models.IntegerField()
    prolific_id = models.StringField(default=str(" "))


def creating_session(subsession: Subsession):
    for i in range(0,len(subsession.get_players())):
        bot_player = subsession.get_players()[i]  # Example: Assigns the first player as the bot
        if i < subsession.session.config['number_of_bots']: 
            bot_player.participant.is_bot = True  # Mark this player as a bot
        else:
            bot_player.participant.is_bot = False  # Mark this player as a human


def get_score(player):
    # List of selected images:
    captcha = [player.captcha1,
               player.captcha2,
               player.captcha3,
               player.captcha4,
               player.captcha5,
               player.captcha6,
               player.captcha7,
               player.captcha8,
               ]
    # print("@@@@ captcha", captcha)
    # List of correct responses:
    correct = [True, False, True, True, False, False, False, True]
    # Compare lists and sum up correct values:

    player.captcha_score = sum([cpt == cor for cpt, cor in zip(captcha, correct)])
    print(player.captcha_score)

class Consent(Page):

    @staticmethod
    def is_displayed(self):
        return self.round_number == 1 and self.participant.vars.get('is_bot') != True

    @staticmethod
    def get_timeout_seconds(player: Player): # Adding timeout for bot to proceed to next page automatically
        if player.participant.is_bot == True:
            return 10  # Set a 10-second timeout for the bot
        return 60 * 2  # Normal timeout for human players

    @staticmethod
    def before_next_page(self, timeout_happened):
        self.prolific_id = self.participant.label

class BotPage(Page):
    @staticmethod
    def is_displayed(self):
        return self.round_number == 1 and self.participant.vars.get('is_bot', False)
    
    @staticmethod
    def get_timeout_seconds(player: Player): # Adding timeout for bot to proceed to next page automatically
        return 10  # Normal timeout for human players
    
    @staticmethod
    def before_next_page(self, timeout_happened):
        self.prolific_id = self.participant.label

class Captcha(Page):
    timeout_seconds = 60
    form_model = 'player'

    def vars_for_template(player):
        # A list with image paths and ids linking to the checkbox!
        images = [
            ['gateway/A1.jpg', 1],
            ['gateway/A2.jpg', 2],
            ['gateway/A3.jpg', 3],
            ['gateway/A4.jpg', 4],
            ['gateway/A5.jpg', 5],
            ['gateway/A6.jpg', 6],
            ['gateway/A7.jpg', 7],
            ['gateway/A8.jpg', 8],
        ]

        random.shuffle(images)
        images = {i: images[i] for i in range(len(images))}
        return {'images': images}

    def get_form_fields(player):
        fields = ['captcha{}'.format(i) for i in range(1, 9)]
        return fields

    # def before_next_page(player, timeout_happened):
    #     # Count score!
    #     get_score(player)


class CaptchaOptOut(Page):

    def is_displayed(player):
        print("captcha_score: ",player.captcha_score)
        return player.captcha_score < 8  # Allow two errors (7 & 8 correct are okay!)


#
# class Instruction(Page):
#     def is_displayed(self):
#         return self.round_number == 1
#
#     @staticmethod
#     def vars_for_template(player: Player):
#         return dict(round=Constants.num_rounds, confCheck=confCheck)
#
# class ComprehensionFail(Page):
#     def is_displayed(self):
#         if self.round_number == 1:
#             return self.isCheck == False
#         else:
#             return False
#
# class Comprehension(Page):
#     form_model = 'player'
#
#     def is_displayed(player: Player):
#         return player.round_number == 1
#
#     def vars_for_template(player: Player):
#             return dict(
#                 num_rounds = Constants.num_rounds,
#                 not_num_rounds = Constants.not_num_rounds
#         )
#
#     @staticmethod
#     def live_method(player,data):
#         if data == 0:
#             player.isCheck = False
#         else:
#             player.isCheck = True

# Consent, Instruction, Comprehension, ComprehensionFail

# Consent,Captcha,CaptchaOptOut
page_sequence = [Consent, BotPage]