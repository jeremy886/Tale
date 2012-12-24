"""
The central town, which is the place where mud players start/log in

'Tale' mud driver, mudlib and interactive fiction framework
Copyright by Irmen de Jong (irmen@razorvine.net)
"""

from __future__ import absolute_import, print_function, division, unicode_literals
from tale.base import Location, Exit, Door, Item, Container
from tale.npc import NPC
from tale.errors import ActionRefused, StoryCompleted
from tale.items.basic import trashcan, newspaper, gem, gameclock, pouch
from tale.util import clone
from tale import globalcontext
from npcs.town_creatures import TownCrier, VillageIdiot, WalkingRat


square = Location("Essglen Town square",
    """
    The old town square of Essglen. It is not much really, and narrow
    streets quickly lead away from the small fountain in the center.
    """)

lane = Location("Lane of Magicks",
    """
    A long straight road leading to the horizon. Apart from a nearby small tower,
    you can't see any houses or other landmarks. The road seems to go on forever though.
    """)

square.exits["north"] = Exit(lane, "A long straight lane leads north towards the horizon.")
square.exits["lane"] = square.exits["north"]

paper = clone(newspaper)
paper.aliases = {"paper"}
paper.short_description = "Last day's newspaper lies on the floor."


class CursedGem(Item):
    def move(self, target, actor, silent=False, is_player=False, verb="move"):
        if self.contained_in is actor and not "wizard" in actor.privileges:
            raise ActionRefused("The gem is cursed! It sticks to your hand, you can't get rid of it!")
        super(CursedGem, self).move(target, actor, verb=verb)


class InsertOnlyBox(Container):
    def remove(self, item, actor):
        raise ActionRefused("The box is cursed! You can't take anything out of it!")


class RemoveOnlyBox(Container):
    def insert(self, item, actor):
        raise ActionRefused("No matter how hard you try, you can't fit %s in the box." % item.title)

insertonly_box = InsertOnlyBox("box1", "box1 (a black box)")
removeonly_box = RemoveOnlyBox("box2", "box2 (a white box)")
normal_gem = clone(gem)
removeonly_box.init_inventory([normal_gem])

cursed_gem = CursedGem("black gem", "a black gem")
cursed_gem.aliases={"gem"}
normal_gem = Item("blue gem", "a blue gem")
normal_gem.aliases={"gem"}
lane.exits["south"] = Exit(square, "The town square lies to the south.")


class WizardTowerEntry(Exit):
    def allow_passage(self, actor):
        if "wizard" in actor.privileges:
            actor.tell("You pass through the force-field.")
        else:
            raise ActionRefused("You can't go that way, the force-field is impenetrable.")

lane.exits["west"] = WizardTowerEntry("wizardtower.hall", "To the west is the wizard's tower. It seems to be protected by a force-field.")


towncrier = TownCrier("laish", "f", title="Laish the town crier", description="The town crier of Essglen is awfully quiet today. She seems rather preoccupied with something.")
towncrier.aliases = {"crier", "town crier"}

idiot = VillageIdiot("idiot", "m", title="blubbering idiot", description="""
    This person's engine is running but there is nobody behind the wheel.
    He is a few beers short of a six-pack. Three ice bricks shy of an igloo.
    Not the sharpest knife in the drawer. Anyway you get the idea: it's an idiot.
    """)

rat = WalkingRat("rat", "n", race="rodent", description="A filthy looking rat. Its whiskers tremble slightly as it peers back at you.")

ant = NPC("ant", "n", race="insect", short_description="A single ant seems to have lost its way.")

clock = clone(gameclock)
clock.short_description = "On the pavement lies a clock, it seems to be working still."

square.init_inventory([cursed_gem, normal_gem, paper, trashcan, pouch, insertonly_box, removeonly_box, clock, towncrier, idiot, rat, ant])


class AlleyOfDoors(Location):
    def notify_player_arrived(self, player, previous_location):
        if previous_location is self:
            player.tell("Weird. That door seemed to go back to the same place you came from.")

alley = AlleyOfDoors("Alley of doors", "An alley filled with doors.")
descr = "The doors seem to be connected to the computer nearby."
door1 = Door(alley, "There's a door marked 'door one'.", long_description=descr, direction="door one", locked=False, opened=True)
door2 = Door(alley, "There's a door marked 'door two'.", long_description=descr, direction="door two", locked=True, opened=False)
door3 = Door(alley, "There's a door marked 'door three'.", long_description=descr, direction="door three", locked=False, opened=False)
door4 = Door(alley, "There's a door marked 'door four'.", long_description=descr, direction="door four", locked=True, opened=False)

alley.add_exits([door1, door2, door3, door4])
alley.exits["first door"] = alley.exits["door one"]
alley.exits["second door"] = alley.exits["door two"]
alley.exits["third door"] = alley.exits["door three"]
alley.exits["fourth door"] = alley.exits["door four"]
alley.exits["north"] = Exit(square, "You can go north which brings you back to the square.")
square.exits["alley"] = Exit(alley, "There's an alley to the south.", "It looks like a very small alley, but you can walk through it.")
square.exits["south"] = square.exits["alley"]


class GameEnd(Location):
    def init(self):
        pass

    def notify_player_arrived(self, player, previous_location):
        # player arrived!
        # The StoryCompleted exception is an immediate game end trigger.
        # This means the player never actually enters this location
        # (because the insert call aborts with an exception)
        # raise StoryCompleted(self.completion)
        player.story_completed(self.completion)
        # setting the status on the player is usually better,
        # it allows the driver to complete the last player action normally.

    def completion(self, player, config, driver):
        player.tell("\n")
        player.tell("This is the game-specific GAME OVER callback.")
        player.tell("It's just here as an example, we now call the normal routine:")
        player.tell("\n")
        driver.story_complete_output(None)


game_end = GameEnd("Game End", "It seems like it is game over!")


class EndDoor(Door):
    def unlock(self, item, actor):
        super(EndDoor, self).unlock(item, actor)
        if not self.locked:
            actor.hints.state("unlocked_enddoor", "The way to freedom lies before you!")

end_door = EndDoor(game_end, "To the east is a door with a sign 'Game Over' on it.", locked=True, opened=False)
end_door.door_code = 999
lane.exits["east"] = end_door
lane.exits["door"] = end_door


class Computer(Item):
    def init(self):
        self.aliases = {"keyboard", "screen", "wires"}

    def allow_item_move(self, actor, verb="move"):
        raise ActionRefused("You can't %s the computer." % verb)

    @property
    def description(self):
        return "It seems to be connected to the four doors. "  \
                + self.screen_text()  \
                + " There's also a small keyboard to type commands. " \
                + " On the side of the screen there's a large sticker with 'say hello' written on it."

    def screen_text(self):
        txt = ["The screen of the computer reads:  \""]
        for door in (door1, door2, door3, door4):
            txt.append(door.name.upper())
            txt.append(": LOCKED. " if door.locked else ": UNLOCKED. ")
        txt.append(" AWAITING COMMAND.\"")
        return "".join(txt)

    def read(self, actor):
        actor.tell(self.screen_text())

    def process_typed_command(self, command, doorname, actor):
        if command == "help":
            message = "KNOWN COMMANDS: LOCK, UNLOCK"
        elif command in ("hi", "hello"):
            message = "GREETINGS, PROFESSOR FALKEN."
        elif command in ("unlock", "lock"):
            try:
                door = self.location.exits[doorname]
            except KeyError:
                message = "UNKNOWN DOOR"
            else:
                if command == "unlock":
                    door.locked = False
                    message = doorname.upper() + " UNLOCKED"
                else:
                    door.locked = True
                    message = doorname.upper() + " LOCKED"
        else:
            message = "INVALID COMMAND"
        actor.tell("The computer beeps quietly. The screen shows: \"%s\"" % message)

    def notify_action(self, parsed, actor):
        if parsed.verb in ("hello", "hi"):
            self.process_typed_command("hello", "", actor)
        elif parsed.verb in ("say", "yell"):
            if "hi" in parsed.args or "hello" in parsed.args:
                self.process_typed_command("hello", "", actor)
            else:
                actor.tell("The computer beeps quietly. The screen shows: \"I CAN'T HEAR YOU. PLEASE TYPE COMMANDS INSTEAD OF SPEAKING.\"  How odd.")

    def handle_verb(self, parsed, actor):
        if parsed.verb == "hack":
            if self in parsed.who_info:
                actor.tell("It doesn't need to be hacked, you can just type commands on it.")
                return True
            elif parsed.who_info:
                raise ActionRefused("You can't hack that.")
            else:
                raise ActionRefused("What do you want to hack?")
        if parsed.verb in ("type", "enter"):
            if parsed.who_info and self not in parsed.who_info:
                raise ActionRefused("You need to type it on the computer.")
            if parsed.message:
                # type "blabla" on computer (message between quotes)
                action, _, door = parsed.message.partition(" ")
                self.process_typed_command(action, door, actor)
                return True
            args = list(parsed.args)
            if self.name in args:
                args.remove(self.name)
            for name in self.aliases:
                if name in args:
                    args.remove(name)
            if args:
                args.append("")
                self.process_typed_command(args[0], args[1], actor)
                return True
        return False


computer = Computer("computer", short_description="A computer is connected to the doors via a couple of wires.")
computer.verbs = {
    # register some custom verbs. You can overwrite existing verbs, so be careful.
    "hack": "Attempt to hack an electronic device.",
    "type": "Enter some text.",
    "enter": "Enter some text.",
}
alley.insert(computer, None)


class DoorKey(Item):
    def notify_moved(self, source_container, target_container, actor):
        player = globalcontext.mud_context.player
        if target_container is player or target_container in player:
            player.hints.state("got_doorkey", "You've found something that might open the exit.")

doorkey = DoorKey("key", description="A key with a little label marked 'Game Over'.")
doorkey.door_code = end_door.door_code
alley.insert(doorkey, None)
