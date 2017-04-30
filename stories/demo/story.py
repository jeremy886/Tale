"""
Demo story.

'Tale' mud driver, mudlib and interactive fiction framework
Copyright by Irmen de Jong (irmen@razorvine.net)
"""
import datetime
import sys
from typing import Optional
from tale.hints import Hint
from tale.story import *
from tale.main import run_story
from tale.player import Player
from tale.driver import Driver


class Story(Storybase):
    name = "Tale Demo"
    author = "Irmen de Jong"
    author_address = "irmen@razorvine.net"
    version = "1.4"
    requires_tale = "3.0"
    supported_modes = {GameMode.IF, GameMode.MUD}
    player_money = 15.5
    money_type = MoneyType.MODERN
    server_tick_method = TickMethod.TIMER
    server_tick_time = 1.0
    gametime_to_realtime = 5
    display_gametime = True
    epoch = datetime.datetime(2012, 4, 19, 14, 0, 0)
    startlocation_player = "town.square"
    startlocation_wizard = "wizardtower.hall"
    license_file = "messages/license.txt"

    driver = None     # will be set by init()

    def init(self, driver: Driver) -> None:
        """Called by the game driver when it is done with its initial initialization"""
        self.driver = driver
        self.driver.load_zones(["town", "wizardtower", "shoppe"])

    def init_player(self, player: Player) -> None:
        """
        Called by the game driver when it has created the player object.
        You can set the hint texts on the player object, or change the state object, etc.
        """
        player.hints.init([
            Hint(None, None, "Find a way to open the door that leads to the exit of the game."),
            Hint("unlocked_enddoor", None, "Step out through the door into the freedom!")
        ])

    def welcome(self, player: Player) -> Optional[str]:
        """welcome text when player enters a new game"""
        player.tell("<bright>Hello, <player>%s</><bright>! Welcome to %s.</>" % (player.title, self.name), end=True)
        player.tell("\n")
        player.tell(self.driver.resources["messages/welcome.txt"].data)
        player.tell("\n")
        return None

    def welcome_savegame(self, player: Player) -> Optional[str]:
        """welcome text when player enters the game after loading a saved game"""
        player.tell("<bright>Hello, <player>%s</><bright>, welcome back to %s.</>" % (player.title, self.name), end=True)
        player.tell("\n")
        player.tell(self.driver.resources["messages/welcome.txt"].data)
        player.tell("\n")
        return None

    def goodbye(self, player: Player) -> None:
        """goodbye text when player quits the game"""
        player.tell("Goodbye, %s. Please come back again soon." % player.title)
        player.tell("\n")

    def completion(self, player: Player) -> None:
        """congratulation text / finale when player finished the game (story_complete event)"""
        player.tell("<bright>Congratulations! You've finished the game!</>")


if __name__ == "__main__":
    # story is invoked as a script, start it in the Tale Driver.
    run_story(sys.path[0])
