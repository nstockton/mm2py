# mm2py
A Python library for reading and modifying [MMapper](https://github.com/mume/mmapper "MMapper GitHub Page") databases

## License
This project is licensed under the terms of the [Unlicense.](https://unlicense.org/UNLICENSE "Unlicense Official Site")

## Credits
Original module written by [Chris Brannon.](https://github.com/CMB "Chris Brannon On GitHub")

Maintained by [Nick Stockton.](https://github.com/nstockton "Nick Stockton On GitHub")

## Installation
If you have Git installed, execute the following command from your console to install or update the library.
```
pip install -U git+https://github.com/nstockton/mm2py.git#egg=mm2py
```

Otherwise, if you do *not* have Git installed, execute the following command  to install or update the library.
```
pip install -U https://github.com/nstockton/mm2py/archive/master.zip#egg=mm2py
```

## Example Usage
```
>>> from mm2.database import Database
>>> db = Database("arda.mm2")
>>> len(db.rooms) # The number of rooms in the database.
27264
>>> db.rooms[0].name # The name of the room with ID 0.
u"Vig's Shop"
>>> db.rooms[0].mob_flags # What mob flags does the room have?
set(['shop'])
>>> db.rooms[0].terrain # How about the terrain?
'city'
>>> db.rooms[0].exits.keys() # What exits does the room have?
['east']
>>> db.rooms[0].exits["east"].exit_flags # What exit flags does the exit have?
set(['exit'])
>>> db.rooms[0].exits["east"].parent.name # The parent property points to the room that this exit belongs to.
u"Vig's Shop"
>>> # Lets try something more complicated. Make a list of room objects, sorted by room ID, which contain exits with one or more of the noblock, nobreak, or nopick door flags set.
>>> results = sorted((room for vnum, room in db.rooms.items() for direction, ext in room.exits.items() if ext.door_flags & {"noblock", "nobreak", "nopick"}), key=lambda room: room.id)
>>> len(results) # How many results?
88
>>> results[0].name # Get the room name of the first result.
u'The Chamber'
>>>
```

There is a lot more that can be done with the library. Python's 'dir' function is your friend.
