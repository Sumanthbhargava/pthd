from otree.api import *
import random
import math


doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'final'
    players_per_group = 6
    num_rounds = 25
    mintemp = 0
    maxtemp=  400
    payoffMultiplier = 5
    payoffDivider = 10


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    feedback = models.LongStringField(blank=True)
    completion_code = models.StringField()


def get_completion_code(player):

    # pre1 = player.participant.incentive_option  # Eventually replace with player goal etc.

    r1 = str(random.randint(100, 999))
    r2 = str(random.randint(100, 999))
    r3 = str(random.randint(100, 999))

    completion_code = "TEMP" + "-" + r1 + "-" + r2 + "-" + r3


    player.completion_code = completion_code



class Debriefing(Page):
    form_fields = ['feedback']
    form_model = 'player'

    timeout_seconds = 120  # time out after 2 minutes to avoid that people linger around.

    @staticmethod
    def before_next_page(player, timeout_happened):
        # Generate a completion code:
        get_completion_code(player)

        # Adjust the payoff:
        part = player.participant

        # if not part.wait_bonus_paid:
        #     part.payoff = 1  # add reward from main game.
        #     part.wait_bonus_paid = True

        # Set to finished:
        # part.finished = True


class CompletionCode(Page):
    def vars_for_template(player):
        part = player.participant
        print("payoffs:: ", part.payoff.to_real_world_currency(player.session))
        return dict(payoff=part.payoff.to_real_world_currency(player.session), session = player.session,)


        # return {
        #     'participation_fee': 123,
        #     'total_payoff': 123
        #     # 'waitpay': part.payment_for_wait.to_real_world_currency(player.session),
        #     # 'total_bonus_mu': part.payoff,
        #     # 'total_bonus_cu': part.payoff.to_real_world_currency(player.session),
        # }

    @staticmethod
    def js_vars(player):
        return dict(
            completionlink=
            player.subsession.session.config['completionlink']
        )


page_sequence = [
    Debriefing,
    CompletionCode
]
