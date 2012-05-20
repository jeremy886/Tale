import datetime

resources = None   # will be set by driver init()


class GameConfig(object):
    name = "Tale Demo"
    author = "Irmen de Jong"
    author_address = "irmen@razorvine.net"
    version = "0.5"                 # arbitrary but is used to check savegames for compatibility
    requires_tale = "0.4"           # tale library required to run the game
    player_name = None              # set a name to create a prebuilt player, None to use the character builder
    player_gender = None            # m/f/n
    player_race = None              # default is "human" ofcourse, but you can select something else if you want
    max_score = 100                 # arbitrary, but when max score is reached, the game is supposed to end. Use 0 or None to disable scoring.
    server_tick_method = "timer"    # 'command' (waits for player entry) or 'timer' (async timer driven)
    server_tick_time = 1.0          # time between server ticks (in seconds) (usually 1.0 for 'timer' tick method)
    gametime_to_realtime = 5        # meaning: game time is X times the speed of real time (only used with "timer" tick method)
    display_gametime = True         # enable/disable display of the game time at certain moments
    epoch = datetime.datetime(2012, 4, 19, 14, 0, 0)    # start date/time of the game clock
    startlocation_player = "town.square"
    startlocation_wizard = "wizardtower.hall"

    def welcome(self, player):
        """welcome text when player enters a new game"""
        player.tell("Welcome to %s." % self.name, end=True)
        player.tell("\n")
        player.tell(resources.load_text("messages/welcome.txt"))
        player.tell("\n")
        player.tell("\n")

    def welcome_savegame(self, player):
        """welcome text when player enters the game after loading a saved game"""
        player.tell("Welcome back to %s." % self.name, end=True)
        player.tell("\n")
        player.tell(resources.load_text("messages/welcome.txt"))
        player.tell("\n")
        player.tell("\n")

    def goodbye(self, player):
        """goodbye text when player quits the game"""
        player.tell("Goodbye, %s. Please come back again soon." % player.title)
        player.tell("\n")

    def completion(self, player):
        """congratulation text / finale when player finished the game (story_complete event)"""
        player.tell("Congratulations! You've finished the game!")


def init(driver):
    global resources
    resources = driver.game_resource