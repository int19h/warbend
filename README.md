# FAQ

## What is WarBend?
WarBend is a Python 2.7 package that lets you load Mount & Blade: Warband saves, inspect them, change them, and write them back to disk. It can also export saves as XML, and re-import it back, allowing tools such as XSLT to be used to perform batch updates.

## I just want to edit a save! Where's my GUI?
You should probably take a look at [WarBender](https://github.com/int19h/WarBender).

## What can WarBend do?

It gives full access to *all* the data stored in a savegame file - every single byte of it. In addition, it provides various convenience features to make that data easy to explore and change programmatically as needed. Here's a simple example to demonstrate what is possible:
```py
from warbend.game.mount_and_blade.native import *
game = load('sg00.sav')

player = game.troops['player']
companions = game.troops['companions']
lords = game.troops['lords']
kings = game.troops['kings']

# All companions ...
for troop in companions:
    # ... are very strong.
    troop.attributes['strength'] = 20
    # ... have maxed-out skills.
    troop.skills[:] = [10] * len(troop.skills)
    # ... have a masterwork long arming sword.
    troop.equipped_items['item_1'].item_kind_id = ID_items.itm_sword_medieval_d_long
    troop.equipped_items['item_1'].modifiers = module_items.imod_masterwork

# All lords ...
for troop in lords:
    # ... have upstanding personality.
    troop.slots['lord_reputation_type'] = module_constants.lrep_upstanding
    # ... love the player.
    troop.slots['troop_player_relation'] = 100
    # ... hate all kings.
    for other in kings:
        troop.slots[other] = -100

save(game, 'sg01.sav')
```

Look at [samples](samples/) for more.

## What does it need to run?

* [Mount & Blade: Warband module system](https://www.taleworlds.com/en/Games/Warband/Download)

* [Python 2.7](http://python.org)

* Packages from [requirements.txt](requirements.txt):
  ```sh
  pip install -r requirements.txt
  ```

## How to run it?

Since it's a library, it cannot be run directly. However, there are some sample scripts provided to get you started. Here's a step-by-step guide:

1. Back up all your savegames, in case something goes wrong. **Do not skip this step!**

1. Download the source code for the package, either using Git, or [directly as a .zip archive](archive/master.zip).

1. Download the module system from the link above, then unpack it into the `modules\Native` folder.
   The resulting directory structure should look like this, where `README.md` is this file:
   ```
    📂
    ├─📂 modules
    ⏐  └─📂 Native
    ⏐     ├─📁 Module_data 1.171
    ⏐     └─📁 Module_system 1.171
    ├─📁 samples
    ├─📁 warbend
    └─📄 README.md
   ```

1. Edit `samples\cheat.cmd`. At the minimum, you will need to set the input and the output file names. By default, it will read from `sg00.sav` (the first save slot) in the usual M&B savegame directory under `Documents`, and write the result to `sg08.sav` (the last save slot) in the same directory.

   **:warning: IT WILL OVERWRITE THE OUTPUT SAVEGAME FILE IF IT EXISTS, WITHOUT ANY WARNING!**

1. Edit `samples\cheat.py` to your taste.

1. Run `samples\cheat.cmd`.

1. Wait for it to complete (it will take about a minute). If you don't see any errors, load the save from the last save slot and enjoy!
