from otree.api import Bot
from otree.api import *
from random import uniform
from otree.api import BaseConstants, widgets
from otree.api import models, Currency
import pickle

result = []

TEMP_CONSTANT = 100

R_CONSTANT = 0
G_CONSTANT = 10
C_CONSTANT = 0
CM = 10
p = 0
x = 0.1
confCheck = True
group1 = []
group2 = []
group3 = []


# to show other players data
# make confidence mandatory
# room temperature
# wording issue

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


class PlayerBot(Bot):
    def play_round(self):
        pass


class Constants(BaseConstants):
    name_in_url = 'Survey'
    players_per_group = None
    num_rounds = 25
    mintemp = 0
    maxtemp=  400
    payoffMultiplier = 5
    payoffDivider = 50
    predError = 10

class Subsession(BaseSubsession):
    def creating_session(self):
        creating_session(self)


def creating_session(subsession: Subsession):
    currRound = subsession.round_number

    if currRound == 1:
        prevTemp = TEMP_CONSTANT
    else:
        actualTemperature = None  # Initialize to None
        for t in subsession.get_players():
            last_round_data = t.in_round(currRound - 1)
            if last_round_data.actualTemperature is not None:
                actualTemperature = last_round_data.actualTemperature
                break

        if actualTemperature is not None:
            prevTemp = actualTemperature
        else:
            prevTemp = TEMP_CONSTANT  # Set a default value

    if p >= uniform(0, 1):
        tempVal = int(prevTemp * (1 - x) + x * uniform(-1, 1) * CM)
        if tempVal < Constants.mintemp:
            tempVal = Constants.mintemp
        elif tempVal > Constants.maxtemp:
            tempVal = Constants.maxtemp
    else:
        tempVal = prevTemp

    for player in subsession.get_players():
        # Assign the calculated temperature to the player's variable
        player.actualTemperature = tempVal


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    temperaturePredict = models.FloatField()
    confidencePredict = models.PositiveIntegerField(min=0, max=10, initial=5)
    # payoff = models.CurrencyField()
    isCheck = models.BooleanField()
    roomTemperature = models.PositiveIntegerField()

    otherPlayerTemp1 = models.FloatField()
    otherPlayerConf1 = models.PositiveIntegerField()
    otherPlayerTemp2 = models.FloatField()
    otherPlayerConf2 = models.PositiveIntegerField()
    otherPlayerTemp3 = models.FloatField()
    otherPlayerConf3 = models.PositiveIntegerField()
    otherPlayerTemp4 = models.FloatField()
    otherPlayerConf4 = models.PositiveIntegerField()
    otherPlayerTemp5 = models.FloatField()
    otherPlayerConf5 = models.PositiveIntegerField()

    actualTemperature = models.PositiveIntegerField()
    q1 = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelectHorizontal,
        label="I often reply on, and act upon, the advice of others.",
        required="required"
    )
    q2 = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelectHorizontal,
        label="I would be the last one to change my opinion in a heated argument on a controversial topic.",
        required="required"
    )
    q3 = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelectHorizontal,
        label="Generally, I'd rather give in and go along for the sake of peace than the struggle to have my way.",
        required="required"
    )
    q4 = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelectHorizontal,
        label="I tend to follow family tradition in making political decisions.",
        required="required"
    )
    q5 = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelectHorizontal,
        label="Basically, my friends are the ones who decide what we do together.",
        required="required"
    )
    q6 = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelectHorizontal,
        label="A charismatic and eloquent speaker can easily influence and change my ideas.",
        required="required"
    )
    q7 = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelectHorizontal,
        label="I am more independent than conforming in my ways.",
        required="required"
    )
    q8 = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelectHorizontal,
        label="If someone is persuasive, I change my opinion and go along with them.",
        required="required"
    )
    q9 = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelectHorizontal,
        label="I don't give in to others easily.",
        required="required"
    )
    q10 = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelectHorizontal,
        label="I tend to rely on others when I have to make an important decision quickly.",
        required="required"
    )
    q11 = models.StringField(
        choices=['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree'],
        widget=widgets.RadioSelectHorizontal,
        label="I like to make my own way in life rather than find a group I can follow.",
        required="required"
    )
    q12 = models.PositiveIntegerField(
        choices=[[1, "1 - Strongly Disagree"], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8],
                 [9, "9 - Strongly Agree"]],
        widget=widgets.RadioSelectHorizontal,
        label="I'd rather depend on myself than others.",
        required="required"
    )
    q13 = models.PositiveIntegerField(
        choices=[[1, "1 - Strongly Disagree"], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8],
                 [9, "9 - Strongly Agree"]],
        widget=widgets.RadioSelectHorizontal,
        label="Winning is everything.",
        required="required"
    )
    q14 = models.PositiveIntegerField(
        choices=[[1, "1 - Strongly Disagree"], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8],
                 [9, "9 - Strongly Agree"]],
        widget=widgets.RadioSelectHorizontal,
        label="I feel good when I cooperate with others. ",
        required="required"
    )

    q16 = models.PositiveIntegerField(
        choices=[[1, "1 - Strongly Disagree"], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8],
                 [9, "9 - Strongly Agree"]],
        widget=widgets.RadioSelectHorizontal,
        label="If a coworker gets a prize, I would feel proud.",
        required="required"
    )
    q17 = models.PositiveIntegerField(
        choices=[[1, "1 - Strongly Disagree"], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8],
                 [9, "9 - Strongly Agree"]],
        widget=widgets.RadioSelectHorizontal,
        label="When another person does better than I do, I get tense and aroused.",
        required="required"
    )
    q18 = models.PositiveIntegerField(
        choices=[[1, "1 - Strongly Disagree"], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8],
                 [9, "9 - Strongly Agree"]],
        widget=widgets.RadioSelectHorizontal,
        label=" It is important to me that I respect the decisions made by my groups.",
        required="required"
    )
    q19 = models.PositiveIntegerField(
        choices=[[1, "1 - Strongly Disagree"], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8],
                 [9, "9 - Strongly Agree"]],
        widget=widgets.RadioSelectHorizontal,
        label="I often do 'my own thing.'",
        required="required"
    )
    q20 = models.PositiveIntegerField(
        choices=[[1, "1 - Strongly Disagree"], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8],
                 [9, "9 - Strongly Agree"]],
        widget=widgets.RadioSelectHorizontal,
        label="To me, pleasure is spending time with others.",
        required="required"
    )
    q21 = models.PositiveIntegerField(
        choices=[[1, "1 - Strongly Disagree"], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8],
                 [9, "9 - Strongly Agree"]],
        widget=widgets.RadioSelectHorizontal,
        label="Parents and children must stay together as much as possible. ",
        required="required"
    )
    q22 = models.PositiveIntegerField(
        choices=[[1, "1 - Strongly Disagree"], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8],
                 [9, "9 - Strongly Agree"]],
        widget=widgets.RadioSelectHorizontal,
        label="The well-being of my coworkers is important to me.",
        required="required"
    )
    q23 = models.PositiveIntegerField(
        choices=[[1, "1 - Strongly Disagree"], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8],
                 [9, "9 - Strongly Agree"]],
        widget=widgets.RadioSelectHorizontal,
        label="Family members should stick together, no matter what sacrifices are required.",
        required="required"
    )
    q24 = models.PositiveIntegerField(
        choices=[[1, "1 - Strongly Disagree"], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8],
                 [9, "9 - Strongly Agree"]],
        widget=widgets.RadioSelectHorizontal,
        label="I rely on myself most of the time; I rarely rely on others.",
        required="required"
    )
    q25 = models.PositiveIntegerField(
        choices=[[1, "1 - Strongly Disagree"], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8],
                 [9, "9 - Strongly Agree"]],
        widget=widgets.RadioSelectHorizontal,
        label="It is my duty to take care of my family, even when I have to sacrifice what I want. ",
        required="required"
    )
    q26 = models.PositiveIntegerField(
        choices=[[1, "1 - Strongly Disagree"], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8],
                 [9, "9 - Strongly Agree"]],
        widget=widgets.RadioSelectHorizontal,
        label="It is important that I do my job better than others.",
        required="required"
    )
    q27 = models.PositiveIntegerField(
        choices=[[1, "1 - Strongly Disagree"], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8],
                 [9, "9 - Strongly Agree"]],
        widget=widgets.RadioSelectHorizontal,
        label="My personal identity, independent of others, is very important to me.",
        required="required"
    )
    q28 = models.StringField(
        label="What do you think was the room temperature in the end of the game?",
        required="required"
    )

    q29 = models.StringField(
        label="What do you think was the average temperature during the game?",
        required="required"
    )
    q30 = models.StringField(
        choices=["It didn't change at all", 'Less than 2 degrees', 'Between 2 and 5 degrees', 'More than 5 degrees'],
        widget=widgets.RadioSelectHorizontal,
        label="How much on average in each round do you think the room temperature changed?",
        required="required"
    )
    q31 = models.StringField(
        label="What do you think was the average of the estimate that you provided during the game?",
        required="required"
    )

    q32 = models.StringField(
        choices=["(0) It does not deviate", 'Less than 2 degrees', 'Between 2 and 5 degrees', 'More than 5 degrees'],
        widget=widgets.RadioSelectHorizontal,
        label="How much do you think on average your prediction deviates from room temperature?",
        required="required"
    )


def other_player(player: Player):
    otherPlayersVal = []
    currRound = player.round_number
    if currRound > 1:
        for i, x in enumerate(player.get_others_in_group()):
            rand = C_CONSTANT * uniform(-1, 1)
            prevVal = x.in_round(currRound - 1)

            try:
                num = int(prevVal.temperaturePredict + rand)
            except TypeError:
                num = None

            try:
                conf = prevVal.confidencePredict
            except TypeError:
                conf = None

            # record the social informatiom
            otherPlayersVal.append({"temp": num, "conf": conf})

            for k in range(player.session.config["players_per_group"]):
                exec(f'player.otherPlayerTemp{k + 1} = {num}')
                exec(f'player.otherPlayerConf{k + 1} = {num}')

    return otherPlayersVal


class ResultsWaitPage(WaitPage):
    group_by_arrival_time = True


class Game(Page):
    form_model = 'player'
    timeout_seconds = 60
    form_fields = ['temperaturePredict']

    @staticmethod
    def live_method(player, data):
        player.confidencePredict = int(data)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            player.temperaturePredict = None
            if player.confidencePredict == 5:
                player.confidencePredict = None
        else:
            player.temperaturePredict = int(player.temperaturePredict + G_CONSTANT * uniform(-1, 1))

    @staticmethod
    def vars_for_template(player: Player):
        print("actual temp: ", player.actualTemperature)
        tempVal = int(player.actualTemperature + R_CONSTANT * uniform(-1, 1))
        player.roomTemperature = tempVal
        return dict(other_player_units=other_player(player), temperature=tempVal, confCheck=confCheck)


class Questionaire1(Page):
    form_model = 'player'
    timeout_seconds = 240
    form_fields = ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10', 'q11']

    def is_displayed(player: Player):
        return player.round_number == Constants.num_rounds


class Questionaire2(Page):
    form_model = 'player'
    timeout_seconds = 240

    form_fields = ['q12', 'q13', 'q14', 'q16', 'q17', 'q18', 'q19', 'q20', 'q21', 'q22', 'q23', 'q24', 'q25',
                   'q26', 'q27']

    def is_displayed(player: Player):
        return player.round_number == Constants.num_rounds

class QuestionaireConsent(Page):
    def is_displayed(player: Player):
        return player.round_number == Constants.num_rounds


class Questionaire3(Page):
    form_model = 'player'
    @staticmethod
    def get_timeout_seconds(player: Player): # Adding timeout for bot to proceed to next page automatically
        if player.participant.is_bot == True:
            return 10  # Set a 10-second timeout for the bot
        return 60 * 2 # Normal timeout for human players

    form_fields = ['q28', 'q29', 'q30', 'q31', 'q32']

    def is_displayed(player: Player):
        return player.round_number == Constants.num_rounds

class LastPage(Page):
    form_model = 'player'

    def is_displayed(player: Player):
        return player.round_number == Constants.num_rounds

    @staticmethod
    def vars_for_template(player: Player):
        # pays = []
        # for i in range(0,player.session.config["num_rounds"]):
        #
        #     try:
        #         pred = player.in_round(i + 1).temperaturePredict
        #         actual = player.in_round(i + 1).acutalTemperature
        #         t = 1 - (abs(pred - actual) / Constants.predError)
        #     except TypeError:
        #         t = 0
        #
        #     pays.append(t)
        #
        # print(pays)
        # payup = round(sum(pays) * Constants.payoffMultiplier, 2)
        part = player.participant
        # part.payoff = payup / Constants.payoffDivider
        # player.payoff = payup
        return dict(payoff=part.payoff.to_real_world_currency(player.session))
    
class Payoff(Page):
    form_model = 'player'
    timeout_seconds = 240

    def is_displayed(player: Player):
        return player.round_number == Constants.num_rounds
    
    def vars_for_template(player):
        final_amount = player.participant.payoff_plus_participation_fee()
        return dict(payoff = final_amount)
        """PAYOFF_PKL_FILE = 'payoff_dict.pkl'
        with open(PAYOFF_PKL_FILE, 'rb') as file:
            payoff_dict = (pickle.load(file))
            payoff = payoff_dict[player.id_in_group]
            return dict(
            payoff=payoff
        )"""

 # Questionaire1, Questionaire2,xx
# QuestionaireConsent,Questionaire3,Questionaire1, Questionaire2
page_sequence = [QuestionaireConsent,Questionaire3, Payoff]