# mm2py

A Python library for reading and modifying [MMapper](https://github.com/mume/mmapper "MMapper GitHub Page") databases.

## License

This project is licensed under the terms of the [Unlicense.](https://unlicense.org/UNLICENSE "Unlicense Official Site")

## Credits

Original module written by [Chris Brannon.](https://github.com/CMB "Chris Brannon On GitHub")

Maintained by [Nick Stockton.](https://github.com/nstockton "Nick Stockton On GitHub")

## Installation

Install the [Python interpreter,](https://python.org "Python Home Page") and make sure it's in your path before running this package.

After Python is installed, execute the following commands from the top level directory of this repository to install the module dependencies.
```
python -m venv .venv
source .venv/bin/activate
pip install --upgrade --require-hashes --requirement requirements-poetry.txt
poetry install --no-ansi
pre-commit install -t pre-commit
pre-commit install -t pre-push
```

## Example Usage

```
>>> from mm2.database import Database
>>> db = Database("arda.mm2")
>>> len(db.rooms) # The number of rooms in the database.
27264
>>> db.rooms[0].name # The name of the room with ID 0.
"Vig's Shop"
>>> db.rooms[0].mob_flags # What mob flags does the room have?
set(['shop'])
>>> db.rooms[0].terrain # How about the terrain?
'city'
>>> db.rooms[0].exits.keys() # What exits does the room have?
['east']
>>> db.rooms[0].exits["east"].exit_flags # What exit flags does the exit have?
set(['exit'])
>>> db.rooms[0].exits["east"].parent.name # The parent property points to the room that this exit belongs to.
"Vig's Shop"
>>> # Lets try something more complicated. Make a list of room objects, sorted by room ID, which contain exits with one or more of the noblock, nobreak, or nopick door flags set.
>>> results = sorted((room for vnum, room in db.rooms.items() for direction, ext in room.exits.items() if ext.door_flags & {"no_block", "no_break", "no_pick"}), key=lambda room: room.id)
>>> len(results) # How many results?
88
>>> results[0].name # Get the room name of the first result.
'The Chamber'
>>>
```

There is a lot more that can be done with the library. Python's 'dir' function is your friend.
