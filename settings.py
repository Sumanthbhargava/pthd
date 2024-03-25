from os import environ


SESSION_CONFIGS = [
    dict(
        name='cooperate_defect_game', display_name="Cooperate Defect Game", app_sequence=['gateway','introduction','waitapp','cooperate_defect_game', 'post_survey','finish'], num_demo_participants=6, past_records_display_condition_1_to_4 = 3, no_of_past_rounds_to_be_displayed = 2, directinteraction = 1, single_stage= False, chatGPT=False, completionlink="https://app.prolific.com/submissions/complete?cc=CTPA66HT"
    ),

    dict(
        name='cooperate_defect_game_test', display_name="Cooperate Defect Game only test", app_sequence=['cooperate_defect_game'], num_demo_participants=4, past_records_display_condition_1_to_4 = 1, no_of_past_rounds_to_be_displayed = 2, directinteraction = 1,  chatGPT=False, completionlink="https://app.prolific.com/submissions/complete?cc=CTPA66HT"
    ),
    dict(
        name='cooperate_defect_game_control', display_name="PTHD Control", app_sequence=['gateway','introduction','waitapp','prisoner', 'post_survey','finish'], num_demo_participants=6, past_records_display_condition_1_to_4 = 1, no_of_past_rounds_to_be_displayed = 2, directinteraction = 1, single_stage = True, chatGPT=False, completionlink="https://app.prolific.com/submissions/complete?cc=CTPA66HT"
    ),
    dict(
        name='cooperate_defect_game_control_test', display_name="PTHD Control test", app_sequence=['prisoner'], num_demo_participants=6,  past_records_display_condition_1_to_4 = 1, no_of_past_rounds_to_be_displayed = 2, directinteraction = 1,  chatGPT=False, completionlink="https://app.prolific.com/submissions/complete?cc=CTPA66HT"
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.01, participation_fee=0.00, doc="", num_rounds=2
)

PARTICIPANT_FIELDS = [
    # GROUPING-RELATED:
    'wait_page_arrival',
    'group_id', 'grouped', 'time_waited', 'payment_for_wait',
    'time_end_waiting1',
    'wait_bonus_paid',
    'drop_grouping',
    # GAME-RELATED:
    #bot flag
    'subgroup',
    # Waiting in game:
    'wait_page_arrival_game',
    # Treatments:
    # 'ef_infop',  # information about the enhancement factor.
    # Counterbalancing:
    'account_main',
    'n_timeout', 'timeout', 'lost', 'group_complete',
    # Variables to collect information from previous rounds:
    'round_info', 'cur_round_info', 'past_round_info', 'past_own_info',
    'past_efs',
    # Posttask:
    'nocomm', 'odd_ef',
    # SVO-RELATED:
    'start_waiting_svo', 'time_waited_svo', 'timeout_svo',
    'svo_angle', 'svo_category',
    # 'svo_selected'
    # oTree HR:
    'finished']
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'GBP'
USE_POINTS = True

ROOMS = [
    dict(
        name='econ101',
        display_name='Econ 101 class',
        #participant_label_file='_rooms/econ101.txt',
    ),
    dict(name='live_demo', display_name='Room for live demo (no participant labels)'),
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""


SECRET_KEY = '5835755321222'

INSTALLED_APPS = ['otree']
