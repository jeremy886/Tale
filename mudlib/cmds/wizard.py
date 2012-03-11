"""
Wizard commands.

Snakepit mud driver and mudlib - Copyright by Irmen de Jong (irmen@razorvine.net)
"""

from __future__ import print_function
import types
import copy
import functools
import sys
from ..errors import SecurityViolation, ParseError, ActionRefused
from .. import baseobjects
from .. import languagetools
from .. import npc
from .. import rooms

all_commands = {}


def wizcmd(command):
    """decorator to add the command to the global dictionary of commands, with a privilege check wrapper"""
    def wizcmd2(func):
        @functools.wraps(func)
        def makewizcmd(player, verb, rest, **ctx):
            if not "wizard" in player.privileges:
                raise SecurityViolation("Wizard privilege required for verb " + verb)
            return func(player, verb, rest, **ctx)
        if command in all_commands:
            raise ValueError("Command defined more than once: "+command)
        all_commands[command] = makewizcmd
        return makewizcmd
    return wizcmd2


@wizcmd("ls")
def do_ls(player, verb, path, **ctx):
    print = player.tell
    if not path.startswith("."):
        raise ActionRefused("Path must start with '.'")
    try:
        module_name = "mudlib"
        if len(path)>1:
            module_name+=path
        __import__(module_name)
        module = sys.modules[module_name]
    except (ImportError, ValueError):
        raise ActionRefused("There's no module named " + path)
    print("<%s>" % path)
    m_items = vars(module).items()
    modules = [x[0] for x in m_items if type(x[1]) is types.ModuleType]
    classes = [x[0] for x in m_items if type(x[1]) is type and issubclass(x[1], baseobjects.MudObject)]
    items = [x[0] for x in m_items if isinstance(x[1], baseobjects.Item)]
    livings = [x[0] for x in m_items if isinstance(x[1], baseobjects.Living)]
    locations = [x[0] for x in m_items if isinstance(x[1], baseobjects.Location)]
    if locations:
        print("Locations: " + ", ".join(locations))
    if livings:
        print("Livings: " + ", ".join(livings))
    if items:
        print("Items: " + ", ".join(items))
    if modules:
        print("Submodules: " + ", ".join(modules))
    if classes:
        print("Classes: " + ", ".join(classes))


@wizcmd("clone")
def do_clone(player, verb, path, **ctx):
    print = player.tell
    if not path:
        raise ParseError("Clone what?")
    if path.startswith("."):
        # find an item somewhere in a module path
        path, objectname = path.rsplit(".", 1)
        if not objectname:
            raise ActionRefused("Invalid object path")
        try:
            module_name = "mudlib"
            if len(path)>1:
                module_name+=path
            __import__(module_name)
            module = sys.modules[module_name]
            obj = getattr(module, objectname, None)
        except (ImportError, ValueError):
            raise ActionRefused("There's no module named " + path)
    else:
        # find an object or living from the inventory or the room
        obj = player.search_item(path)
        if not obj:
            obj = player.location.search_living(path)
    # clone it
    if not obj:
        raise ActionRefused("Object not found")
    elif isinstance(obj, baseobjects.Item):
        item = copy.deepcopy(obj)
        player.inventory.add(item)
        print("Cloned: " + repr(item))
        player.location.tell("{player} conjures up {item}, and quickly pockets it."
                             .format(player=languagetools.capital(player.title),
                                     item=languagetools.a(item.title)),
                             exclude_living=player)
    elif isinstance(obj, npc.NPC):
        clone = copy.deepcopy(obj)
        clone.cpr()  # (re)start heartbeat
        print("Cloned: " + repr(clone))
        player.location.tell("{player} summons {npc}."
                             .format(player=languagetools.capital(player.title),
                                     npc=languagetools.a(clone.title)),
                             exclude_living=player)
        player.location.enter(clone)
    else:
        raise ActionRefused("Can't clone "+languagetools.a(obj.__class__.__name__))


@wizcmd("destroy")
def do_destroy(player, verb, arg, **ctx):
    # @todo: ask for confirmation (async)
    print = player.tell
    if not arg:
        raise ParseError("Destroy what?")
    victim = player.search_item(arg)
    if victim:
        if victim in player.inventory:
            player.inventory.remove(victim)
        else:
            player.location.remove_item(victim)
        victim.destroy(ctx)
    else:
        # maybe there's a living here instead
        victim = player.location.search_living(arg)
        if victim:
            if victim is player:
                raise ActionRefused("You can't destroy yourself, are you insane?!")
            victim.tell("%s creates a black hole that sucks you up. You're utterly destroyed." % languagetools.capital(player.title))
            victim.destroy(ctx)
        else:
            raise ActionRefused("There's no %s here." % arg)
    print("You destroyed %r." % victim)
    player.location.tell("{player} makes some gestures and a tiny black hole appears.\n"
                         "{victim} disappears in it, and the black hole immediately vanishes."
                         .format(player=languagetools.capital(player.title),
                                 victim=languagetools.capital(victim.title)),
                         exclude_living=player)


@wizcmd("pdb")
def do_pdb(player, verb, rest, **ctx):
    import pdb
    pdb.set_trace()   # @todo: remove this when going multiuser (I don't think you can have a synchronous debug session anymore)


@wizcmd("wiretap")
def do_wiretap(player, verb, arg, **ctx):
    print = player.tell
    if not arg:
        print("Installed wiretaps:", ", ".join(str(tap) for tap in player.installed_wiretaps) or "none")
        print("Use 'wiretap .' or 'wiretap living' to tap the room or a living.")
        print("Use 'wiretap -clear' to remove all your wiretaps.")
        return
    if arg == ".":
        player.create_wiretap(player.location)
        print("Wiretapped room '%s'." % player.location.name)
    elif arg == "-clear":
        player.installed_wiretaps.clear()
        print("All wiretaps removed.")
    else:
        living = player.location.search_living(arg)
        if living:
            if living is player:
                raise ActionRefused("Can't wiretap yourself.")
            player.create_wiretap(living)
            print("Wiretapped %s." % living.name)
        else:
            raise ActionRefused(arg, "isn't here.")


@wizcmd("teleport")
def do_teleport(player, verb, args, **ctx):
    if not args:
        raise ActionRefused("Usage: teleport [to] [.module.path.to.object | playername | @start]")
    teleport_self = False
    if args.startswith("to "):
        teleport_self = True
        args = args.split(None, 1)[1]
    if args.startswith("."):
        # teleport player to a location somewhere in a module path
        path, objectname = args.rsplit(".", 1)
        if not objectname:
            raise ActionRefused("Invalid object path")
        try:
            module_name = "mudlib"
            if len(path)>1:
                module_name += path
            __import__(module_name)
            module = sys.modules[module_name]
        except (ImportError, ValueError):
            raise ActionRefused("There's no module named " + path)
        target = getattr(module, objectname, None)
        if not target:
            raise ActionRefused("Object not found")
        if teleport_self:
            if isinstance(target, baseobjects.Living):
                target = target.location  # teleport to target living's location
            if not isinstance(target, baseobjects.Location):
                raise ActionRefused("Can't determine location to teleport to.")
            teleport_to(player, target)
        else:
            teleport_someone_to_player(target, player)
    else:
        # target is a player (or @start - the wizard starting location)
        if args=="@start":
            teleport_to(player, rooms.STARTLOCATION_WIZARD)
        else:
            target = ctx["driver"].search_player(args)
            if not target:
                raise ActionRefused("%s isn't here." % args)
            if teleport_self:
                teleport_to(player, target.location)
            else:
                teleport_someone_to_player(target, player)


def teleport_to(player, location):
    """helper function for teleport command, to teleport the player somewhere"""
    print = player.tell
    player.location.tell("%s makes some gestures and a portal suddenly opens." %
                         languagetools.capital(player.title), exclude_living=player)
    player.location.tell("%s jumps into the portal, which quickly closes behind %s." %
                         (languagetools.capital(player.subjective), player.objective), exclude_living=player)
    # Can't use player.move() because we want to override any access checks.
    player.location.livings.remove(player)
    player.location = location
    location.livings.add(player)
    print("You've been teleported.")
    print(player.look())
    location.tell("Suddenly, a shimmering portal opens!", exclude_living=player)
    location.tell("%s jumps out, and the portal quickly closes behind %s." %
                  (languagetools.capital(player.title), player.objective), exclude_living=player)


def teleport_someone_to_player(who, player):
    """helper function for teleport command, to teleport someone to the player"""
    who.location.tell("Suddenly, a shimmering portal opens!")
    room_msg = "%s is sucked into it, and the portal quickly closes behind %s." % (languagetools.capital(who.title), who.objective)
    who.location.tell(room_msg, specific_targets=[who], specific_target_msg="You are sucked into it!")
    who.location.livings.remove(who)
    who.location = player.location
    player.location.livings.add(who)
    player.location.tell("%s makes some gestures and a portal suddenly opens." %
                         languagetools.capital(player.title), exclude_living=who)
    player.location.tell("%s tumbles out of it, and the portal quickly closes again." %
                         languagetools.capital(who.title), exclude_living=who)
