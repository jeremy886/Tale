"""
Setup script for distutils

'Tale' mud driver, mudlib and interactive fiction framework
Copyright by Irmen de Jong (irmen@razorvine.net)
"""
import tale
try:
    # try setuptools first, to get access to build_sphinx and test commands
    from setuptools import setup
    using_setuptools = True
except ImportError:
    from distutils.core import setup
    using_setuptools=False

print("version="+tale.__version__)

setup_args = dict(
    name='tale',
    version=tale.__version__,
    packages=['tale', 'tale.cmds', 'tale.items', 'tale.messages', 'tale.rooms'],
    package_data={
        'tale': ['soul_adverbs.txt', 'messages/*']
        },
    url='http://packages.python.org/tale',
    license='GPL v3',
    author='Irmen de Jong',
    author_email='irmen@razorvine.net',
    description='Mud, mudlib & interactive fiction framework',
    long_description="""Tale is a framework for creating mudlibs, muds and/or interactive fiction (text adventures).

It's still being designed and new features are implement along the way,
but the current version contains a runnable minimalistic mud world that you
can explore. Start it by running the driver; ``python -m tale.driver``
(or use the supplied launch script, ``tale-driver``).
""",
    keywords="mud, mudlib, interactive fiction, text adventure",
    scripts=["tale-driver.cmd", "tale-driver"],
    platforms="any",
    classifiers= [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Topic :: Communications :: Chat",
        "Topic :: Games/Entertainment",
        "Topic :: Games/Entertainment :: Multi-User Dungeons (MUD)"
    ]
)

if using_setuptools:
    setup_args["test_suite"]="nose.collector"    # use Nose to run unittests

setup(**setup_args)