import random

from otree.api import *
import csv
import math
doc = """
Your app description
"""
def read_csv():
    with open('post_survey/SVO.csv', encoding='utf-8-sig') as f:
        return [
            dict(
                round_number=int(row['round_number']),
                to_self=int(row['to_self']),
                to_other=int(row['to_other']),
            )
            for row in csv.DictReader(f)
        ]


def group_rows():
    from collections import defaultdict

    d = defaultdict(list)
    for row in read_csv():
        round_number = row['round_number']
        d[round_number].append(row)
    return d

class C(BaseConstants):
    NAME_IN_URL = 'Survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 19
    CHART_TEMPLATE = 'post_survey/chart.html'
    INSTRUCTIONS_TEMPLATE = 'post_survey/instructions.html'
    ROWS = group_rows()

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

def make_field(label):
    return models.IntegerField(
        choices=[
        [1, "Strongly Disagree"],
        [2, "Disagree"],
        [3, "Neither Disagree nor Agree"],
        [4, "Agree"],
        [5, "Strongly Agree"]],
        label=label,
        widget=widgets.RadioSelectHorizontal
    )

def make_field9(label):
    return models.IntegerField(
        choices=[
        [1, "1 - Strongly Disagree"],
        [2, "2"],
        [3, "3"],
        [4, "4"],
        [5, "5"],
        [6, "6"],
        [7, "7"],
        [8, "8"],
        [9, "9 - Strongly Agree"]],
        label=label,
        widget=widgets.RadioSelectHorizontal
    )


class Player(BasePlayer):
    neut_1 = make_field('In many cases you have no choice but to break the rules')
    neut_2 = make_field('Often, breaking the rules does no harm.')
    neut_3 = make_field("When someone gets hurt because one breaks the rules, they usually deserve it.")
    neut_4 = make_field('Most people who criticise you for breaking the rules constantly break the rules themselves')
    neut_5 = make_field('Sometimes you have to break the rules to help the people you care about.')
    pun_above = make_field9('I reduced the income of those who contributed above the group average.')
    pun_below = make_field9('I reduced the income of those who contributed below the group average.')
    pun_rand = make_field9('I reduced the income of those who contributed either below or above the group average.')
    pun_dif = make_field9('I reduced the income of those who contributed differently from me.')
    criteria = models.LongStringField(blank=True, label="What were your criteria to reduce other players' income?")
    choice = models.IntegerField(choices=list(range(9)))
    timeout = models.BooleanField(initial=False)
    angle = models.FloatField()
    category = models.StringField()
    risk = models.IntegerField(choices=[[1, "50 percent chance of winning 30 MU and 50 percent to win nothing"],
                                          [2, "The sure payment"]],
                               label="What would you prefer:",
                               widget=widgets.RadioSelectHorizontal)

    perceived_noise = models.IntegerField(choices=[[1, "Between 0 and 6 Money Units"],
                                                   [2, "Between 1 and 5 Money Units"],
                                                   [3, "Between 2 and 4 Money Units"]
                                                   ],
                                          label="In one of the groups in the experiment,"
                                                " each Money Unit you spent to reduce other players' income resulted"
                                                " in a amount of Money Units selected at random.\n"
                                                "Out of which of the following number ranges do you think this amount was drawn?",
                                          widget=widgets.RadioSelect
                                          )
    avg_pun_paid = models.IntegerField(blank=True, label="On average per each round, how many reduction points do you think you have paid to reduce others' income?")
    avg_pun_rec = models.IntegerField(blank=True, label="On average per each round, how much do you think your income has been reduced by others?")
    avg_con = models.IntegerField(blank=True, label="On average per each round, how much do you think you have contributed?")
    opt_con = models.IntegerField(blank=True, label="How many points do you think was an appropriate contribution per round?")
    exp = models.IntegerField(choices=[
        [1, "I have played a similar task in more than one previous study."],
        [2, "I have played a similar task in one previous study."],
        [3, "I have never played a similar task before."],
    ],
        label="Do you have any previous experience with the kind of contribution task you played?",
        widget=widgets.RadioSelect)
    comments = models.LongStringField(blank=True, label="Do you have any other comments on the study? (optional)")

# FUNCTIONS
def assign_category(angle):
    if angle > 57.15:
        return 'Altruistic'
    if angle > 22.45:
        return 'Prosocial'
    if angle > -12.04:
        return 'Individualistic'
    return 'Competitive'

# PAGES
class Intro(Page):
    form_model = "player"
    timeout_seconds = 120
    @staticmethod
    def is_displayed(player: Player):
        if player.session.config["name"] == "survey":
            player.participant.group_end = False
        return player.round_number == 1


class Decide(Page):
    form_model = 'player'
    form_fields = ['choice']

    @staticmethod
    def is_displayed(player):
        return player.round_number < C.NUM_ROUNDS - 3
    @staticmethod
    def js_vars(player: Player):
        return dict(rows=C.ROWS[player.round_number])

    @staticmethod
    def get_timeout_seconds(player):
        if player.round_number < 2:
            return 60
        else:
            return 30

    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.timeout = True
        if player.round_number == C.NUM_ROUNDS - 4:
            participant = player.participant
            to_self_total = 0
            to_other_total = 0
            rows = []
            for p in player.in_all_rounds():
                row = C.ROWS[p.round_number][p.choice]
                to_self_total += row['to_self']
                to_other_total += row['to_other']
                rows.append(row)
            payout_row = random.choice(rows)
            participant.svo_payout_self = payout_row["to_self"]/5
            participant.svo_payout_other = payout_row["to_other"]/5
            avg_self = to_self_total / C.NUM_ROUNDS
            avg_other = to_other_total / C.NUM_ROUNDS
            radians = math.atan((avg_other - 50) / (avg_self - 50))
            participant.svo_angle = round(math.degrees(radians), 2)
            participant.svo_category = assign_category(participant.svo_angle)


class ResultsSVO(Page):
    timeout_seconds = 30
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 15


class RiskIntro(Page):
    form_model = "player"
    timeout_seconds = 60

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 15

class Risk(Page):
    form_model = "player"
    form_fields = ["risk"]
    timeout_seconds = 45

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number > 14

    @staticmethod
    def vars_for_template(player):
        if player.round_number == 15:
            player.participant.sure_payment = 16
        return dict(
            sure_payment=player.participant.sure_payment,
            task_nr=player.round_number - 14
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.round_number < C.NUM_ROUNDS:
            sure_payment = player.participant.sure_payment
            risk_task = 18 - player.round_number
            sure_change = 2 ** risk_task
            if player.risk == 1:
                sure_payment += sure_change
            else:
                sure_payment -= sure_change
            player.participant.sure_payment = sure_payment

        else:
            if player.risk == 1:
                player.participant.risk_payout = random.choice([0, 30])
            else:
                player.participant.risk_payout = player.participant.sure_payment



class ResultsRisk(Page):
    timeout_seconds = 30

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS




class Neut(Page):
    form_model = "player"
    form_fields = ["neut_1", "neut_2", "neut_3", "neut_4", "neut_5"]
    timeout_seconds = 120
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

class Survey(Page):
    form_model = "player"
    form_fields = ["pun_above", "pun_below", "pun_rand", "pun_dif", "criteria"]
    timeout_seconds = 180
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

class Survey2(Page):
    form_model = "player"
    form_fields = ["avg_pun_paid", "avg_pun_rec", "avg_con", "opt_con", "perceived_noise", "exp", "comments"]
    timeout_seconds = 120
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [Neut, Survey, Survey2]
