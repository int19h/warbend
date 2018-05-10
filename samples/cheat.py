from __future__ import absolute_import, division, print_function

from random import randint
from sys import argv, maxint, stderr

import locale
locale.setlocale(locale.LC_ALL, '') # pretty printing for numbers

from warbend.game.mount_and_blade.native import * # pylint: disable=W0614
game = load(argv[1])

# from warbend.serialization import xml
# save(game, argv[1] + '.xml', format=xml)
# game = load(argv[1] + '.xml', format=xml)

with transaction(game):
    print('Changing game data ...', file=stderr)

    player = game.troops['player']
    companions = set(game.troops['companions'])
    kings = set(game.troops['kings'])
    lords = set(game.troops['lords'])
    ladies = set(game.troops['kingdom_ladies'])

    game.global_variables['player_honor'] = 100
    game.global_variables['player_right_to_rule'] = 100

    player.slots['troop_renown'] = 5000

    # Some fancy gear for player and companions:
    for troop in {player} | companions:
        troop.equipped_items['head'].item_kind_id = ID_items.itm_winged_great_helmet
        troop.equipped_items['head'].modifier = module_items.imod_lordly
        troop.equipped_items['body'].item_kind_id = ID_items.itm_plate_armor
        troop.equipped_items['body'].modifier = module_items.imod_lordly
        troop.equipped_items['foot'].item_kind_id = ID_items.itm_plate_boots
        troop.equipped_items['foot'].modifier = module_items.imod_lordly
        troop.equipped_items['gloves'].item_kind_id = ID_items.itm_gauntlets
        troop.equipped_items['gloves'].modifier = module_items.imod_lordly
        troop.equipped_items['horse'].item_kind_id = ID_items.itm_charger
        troop.equipped_items['horse'].modifier = module_items.imod_champion
        troop.equipped_items['item_0'].item_kind_id = ID_items.itm_hafted_blade_a
        troop.equipped_items['item_0'].modifier = module_items.imod_masterwork
        #troop.equipped_items['item_1'].item_kind_id = ID_items.itm_tab_shield_round_e
        #troop.equipped_items['item_1'].modifier = module_items.imod_reinforced
        #troop.equipped_items['item_1'].item_kind_id = ID_items.itm_sword_medieval_d_long
        troop.equipped_items['item_1'].item_kind_id = ID_items.itm_morningstar
        troop.equipped_items['item_1'].modifier = module_items.imod_masterwork
        troop.equipped_items['item_2'].item_kind_id = ID_items.itm_hunting_bow
        troop.equipped_items['item_2'].modifier = module_items.imod_masterwork
        troop.equipped_items['item_3'].item_kind_id = ID_items.itm_bodkin_arrows
        troop.equipped_items['item_3'].modifier = module_items.imod_large_bag

    # All companions have max level and high stats.
    for troop in companions:
        troop.level = 61
        troop.experience = 640000000
        troop.attributes['strength'] = 200
        troop.attributes['agility'] = 200
        troop.attributes['intelligence'] = 1000
        troop.attributes['charisma'] = 1000
        troop.proficiencies[:] = [699] * len(troop.proficiencies)
        troop.skills[:] = [10] * len(troop.skills)

    # All lords and companions (when they become lords) are upstanding.
    for troop in (lords | companions):
        troop.slots['lord_reputation_type'] = module_constants.lrep_upstanding

    # All lords and companions are rich.
    for troop in (lords | companions):
        troop.slots['troop_wealth'] = 1000000000

    # All lords have high agility.
    for troop in lords:
        troop.attributes['agility'] = 50

    # All lords have maxed out skills.
    for troop in lords:
        troop.skills[:] = [10] * len(troop.skills)

    # All characters love the player.
    for troop in game.troops:
        try:
            troop.slots['troop_player_relation'] = 100
        except IndexError:
            pass

    # All lords love each other.
    for troop1 in lords:
        for troop2 in lords:
            troop1.slots[troop2] = 100

    # All lords are indifferent to all kings, and vice versa.
    for troop in lords:
        for king in kings:
            troop.slots[king] = 0
            king.slots[troop] = 0

    # Scramble random decision seed for all lords (changes persuasion result),
    # and reset their intrigue impatience ("weary of politics").
    for troop in lords:
        troop.slots['troop_set_decision_seed'] = randint(0, maxint)
        troop.slots['troop_temp_decision_seed'] = randint(0, maxint)
        troop.slots['troop_intrigue_impatience'] = 0

    # All locations love the player.
    # All locations are prosperous.
    for party in game.parties:
        if party.valid:
            try:
                party.slots['center_player_relation'] = 100
            except IndexError:
                pass
            try:
                party.slots['town_prosperity'] = 100
            except IndexError:
                pass

save(game, argv[2])
