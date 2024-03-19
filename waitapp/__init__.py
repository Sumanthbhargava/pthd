from otree.api import *
import random
import time

doc = """
This app is built to collect waiting players and delivers a check in the end
to only advance players who are still attenttive.
It may drop or keep all of the remaining players.
In the following app this behavior needs to be set.
"""


class C(BaseConstants):
    NAME_IN_URL = 'waitapp'
    PLAYERS_PER_GROUP = None


    GROUPSIZE_S1 = 4  # minimum groupsize.
    NUM_ROUNDS = 25
    GROUPING_TIMEOUT = 1800 # 120  # should be eventually: 10 min? 8min? 600 (or 300?)
    MAXWAIT_PAY = 40 / 0.6  # maximum wait bonus.


    MAXTIME_PROMPT = 300


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    gid_wait = models.IntegerField()


class Player(BasePlayer):
    grouping_timeout = models.FloatField(blank=True)
    max_wait_reached = models.BooleanField(inital=False)  # has a player waited until the end?
    completion_codew = models.StringField(blank=True)


# -------------------------------------------------------------------------------------------------------------------- #
#
# FUNCTIONS
#
# -------------------------------------------------------------------------------------------------------------------- #


def creating_session(subsession):
    for player in subsession.get_players():
        player.max_wait_reached = False
        player.completion_codew = "Waiting"
        player.participant.wait_bonus_paid = False

        player.participant.grouped = False  # may eventually not be needed anymore!
        player.participant.group_id = 0  # all start as ungrouped.
        player.participant.drop_grouping = False
        player.participant.finish_waitapp = False


# -------------------------------------------------------------------------------------------------------------------- #
# --------------- GROUPING FUNCTIONS in dependence of waiting time --------------------------------------------------- #
# -------------------------------------------------------------------------------------------------------------------- #


def waiting_seconds(player):
    participant = player.participant

    wait = int(time.time() - participant.wait_page_arrival)  # seconds waiting since participant wait page arrival
    player.participant.time_waited = wait  # save current waiting time.

    return wait


def ranked_waiting_seconds(waiting_players):
    waits = [waiting_seconds(p) for p in waiting_players if not p.max_wait_reached]
    waits.sort(reverse=True)
    return waits


"""def group_by_arrival_time_method(subsession, waiting_players):
    # 1. Get all players who are on the waitpage and actually still wait:
    waiters = [wpl for wpl in waiting_players if not wpl.max_wait_reached]
    # 2. Get their ranked waiting times (index 0 is the largest)
    wait_times = ranked_waiting_seconds(waiters)  # call ranked_waiting_seconds function
    # 3. Get the number of waiting players:
    nwaiters = len(wait_times)  # call this afterwards, since the ranking disregards those who are finsihed.

    # Number of bots to include in each group as specified in session config
    num_bots = subsession.session.config.get('number_of_bots', 1)
    # Ensure the number of bots does not exceed the limit for the group
    num_bots = min(num_bots, C.GROUPSIZE_S1 - 1)

    # Separate waiting players into bots and humans based on 'is_bot' attribute
    bot_players = [p for p in waiting_players if p.participant.vars.get('is_bot', False)]
    human_players = [p for p in waiting_players if not p.participant.vars.get('is_bot', False)]

    # Check if there are enough humans and bots waiting to form a complete group
    if len(human_players) >= C.GROUPSIZE_S1 - num_bots and len(bot_players) >= num_bots:
        # Select the required number of bots and fill the rest of the group with humans
        selected_bots = bot_players[:num_bots]
        selected_humans = human_players[:(C.GROUPSIZE_S1 - num_bots)]
        # Return the selected players to form a new group
        return selected_bots + selected_humans"""

def group_by_arrival_time_method(subsession, waiting_players):
    # 1. Get all players who are on the waitpage and actually still wait:
    waiters = [wpl for wpl in waiting_players if not wpl.max_wait_reached]
    # 2. Get their ranked waiting times (index 0 is the largest)
    wait_times = ranked_waiting_seconds(waiters)  # call ranked_waiting_seconds function
    # 3. Get the number of waiting players:
    nwaiters = len(wait_times)  # call this afterwards, since the ranking disregards those who are finsihed.

    print("@@@@ Waiting times are", wait_times)
    print("@@@@ number of players waiting:", nwaiters)

    # Determine whether a group can be formed according to constraints:
    # Make group size into var:
    gsize = C.GROUPSIZE_S1
    if nwaiters >= gsize:  # test for if minimum number is there:
        print("@@@@ minimum number reached.",
              "Maximum time:", wait_times[0])

        cur_group_id = max([p.participant.group_id for p in subsession.get_players()])

        # Make sure that players who wait longest are grouped with priority:
        ordered_waiters = [x for _, x in sorted(zip(wait_times, waiters))]
        # print("@@@@ ordered_waiters", ordered_waiters)
        # grouped_players = ordered_waiters[0:((nwaiters // gsize) * gsize)]  # the largest multiple of 5.
        grouped_players = ordered_waiters  # the largest multiple of 5.

        # Decide on whether all available players should be grouped or only the first multiple of 5.
        # Yes, because then we get the largest possible number of people;
        # if some missed the start in different groups, we would lose more than if we pipe all and take what we get.

        # Sample condition:
        # ef_info = random.choice([True, False])

        # Loop over all to-be grouped players if a group can be formed.
        for pwait in grouped_players:
            pwait.participant.grouped = True
            paywait = pwait.participant.time_waited / C.GROUPING_TIMEOUT * C.MAXWAIT_PAY
            paywait = paywait if paywait < C.MAXWAIT_PAY else C.MAXWAIT_PAY
            pwait.participant.payment_for_wait = cu(paywait)
            # Note: roughly one cent per second adding up to 50 cents for ten minutes.

            # Assign persistent group id (participant vars!) for use in next app:
            pwait.participant.group_id = cur_group_id + 1

            # Save time of finishing group check:
            pwait.participant.time_end_waiting1 = time.time()

        return grouped_players  # return the waiting players.

    # Finishers:
    longwaits = [wpl for wpl in waiting_players if
                 waiting_seconds(wpl) > C.GROUPING_TIMEOUT and not wpl.participant.wait_bonus_paid]
    # print("@@@@ longwaits", longwaits)

    # Are there any longwaits?
    if len(longwaits) > 0:

        # Loop over longwaits, assign their payment and set inactive.
        for lw in longwaits:
            lwpart = lw.participant

            lwpart.grouped = False
            # print("@@@@ time waited", lw.participant.time_waited)
            paywait = lwpart.time_waited / C.GROUPING_TIMEOUT * C.MAXWAIT_PAY
            # print("@@@@ payoff", paywait)
            paywait = paywait if paywait < C.MAXWAIT_PAY else C.MAXWAIT_PAY
            # We could also set paywait to C.MAXWAIT_PAY here.
            lwpart.payment_for_wait = cu(paywait)
            lwpart.payoff = cu(paywait)
            lwpart.wait_bonus_paid = True  # flag to prevent re-execution.

            # Set to finished:
            lwpart.finished = True


# -------------------------------------------------------------------------------------------------------------------- #
# PAGES -------------------------------------
# -------------------------------------------------------------------------------------------------------------------- #
class WaitGroupingPage(WaitPage):
    template_name = 'waitapp/WaitGrouping.html'
    body_text = ""
    group_by_arrival_time = True

    # Only displayed in round 1
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

    # Variables for display:
    @staticmethod
    def js_vars(player: Player):
        return dict(timewaited=player.participant.time_waited,
                    maxwait=player.max_wait_reached,
                    maxbonus=C.MAXWAIT_PAY,
                    grouptimeout=C.GROUPING_TIMEOUT,
                    )  # This grouping timeout time is set in Constants

    @staticmethod
    def vars_for_template(player: Player):
        now = time.time()

        maxtime = player.participant.wait_page_arrival + C.GROUPING_TIMEOUT

        if now > maxtime:
            player.max_wait_reached = True  # if a player is above the time classify as reaching the maximum wait time.
            # player.payoff = 25 # take away the payment that someone gets for waiting

        waitpay = cu(player.participant.payoff).to_real_world_currency(player.session)

        return dict(
            timeout=maxtime,
            participation_fee=player.session.config['participation_fee'],
            total_payoff=player.session.config['participation_fee'] + waitpay,
            waitpay=waitpay,
            total_money=player.participant.payoff_plus_participation_fee()
        )

    # Save the ID of waiters:
    @staticmethod
    def after_all_players_arrive(group: Group):
        p1 = group.get_player_by_id(1)
        group.gid_wait = p1.participant.group_id  # save the group ID to have it for dropped out groups too!


# Prompt from Miriam:
class GroupCheck(Page):
    @staticmethod
    def get_timeout_seconds(player: Player): # Adding timeout for bot to proceed to next page automatically
        if player.participant.is_bot == True:
            return 10  # Set a 10-second timeout for the bot
        return 60 * 5 # Normal timeout for human players


    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1  # and player.max_wait_reached is False

    @staticmethod
    def before_next_page(player, timeout_happened):
        participant = player.participant

        # this is needed for timeout_seconds Timeout... the countdown that counts down on the page
        if timeout_happened:
            # If player fails to respond count as dropped out and dropped grouping (redundant?).
            # TODO: Possible redundancy; likely can be dropped; could however serve documentation purposes!
            # player.dropped_out = True
            if participant.is_bot == False:
                participant.drop_grouping = True

        # Get starting time:
        participant.wait_page_arrival_game = time.time()


class FailedToRespondGrouping(Page):

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.drop_grouping is True

# WaitGroupingPage, GroupCheck, FailedToRespondGrouping
page_sequence = [ WaitGroupingPage, GroupCheck, FailedToRespondGrouping]
