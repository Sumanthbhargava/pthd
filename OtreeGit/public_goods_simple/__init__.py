from otree.api import *
import random


class C(BaseConstants):
    NAME_IN_URL = 'public_goods_simple'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 4
    ENDOWMENT = cu(100)
    #MULTIPLIER = 1.8


class Subsession(BaseSubsession):
    pass

def creating_session(subsession: Subsession):
    print("Executing creating_session")
    # Set a random multiplier for the current round
    subsession.session.vars['multiplier'] = round(random.uniform(0, 4), 1)
    subsession.session.vars['last_multiplier'] = -1
    for player in subsession.get_players():
            print("Setting player endowment")
            player.participant.vars['endowment'] = C.ENDOWMENT



class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()


class Player(BasePlayer):
    contribution = models.CurrencyField(
        min=0, label="How much will you contribute?"
    )

# FUNCTIONS
def set_payoffs(group: Group):
    multiplier = group.subsession.session.vars['multiplier']
    players = group.get_players()
    contributions = [p.contribution for p in players]
    group.total_contribution = sum(contributions)
    group.individual_share = (
        group.total_contribution * multiplier / C.PLAYERS_PER_GROUP
    )
    for p in players:
        if p.round_number == 1:
            p.payoff = C.ENDOWMENT - p.contribution + group.individual_share
            p.participant.vars['endowment']=p.payoff
            print(p.participant.vars)
        else:
            p.payoff = p.participant.vars['endowment'] - p.contribution + group.individual_share
            p.participant.vars['endowment']=p.payoff
            print(p.participant.vars)

        
    group.subsession.session.vars['last_multiplier']= multiplier
    group.subsession.session.vars['multiplier']=round(random.uniform(0, 4), 1)
    print(group.subsession.session.vars)


# PAGES
class Contribute(Page):
    def is_displayed(self):
        print("Contribute page is being displayed")
        print(self)
        return True
    form_model = 'player'
    form_fields = ['contribution']
    def before_next_page(self, timeout_happened):
        # Ensure the contribution does not exceed the player's endowment
        if self.contribution > self.participant.vars['endowment']:
            self.contribution = self.participant.vars['endowment']
    
    def vars_for_template(self):
        # Get the player's past contributions, safely handling potential None values
        past_contributions = [p.field_maybe_none('contribution') for p in self.in_all_rounds()]

        # Filter out None values
        past_contributions = [c for c in past_contributions if c is not None]

        # Get the last two contributions
        last_two_contributions = past_contributions[-2:]

        return {
            #'last_two_contributions': last_two_contributions
            'past_contributions' : past_contributions
        }

class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    pass


page_sequence = [Contribute, ResultsWaitPage, Results]
