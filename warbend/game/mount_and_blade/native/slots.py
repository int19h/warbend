from __future__ import absolute_import, division, print_function

from ....data import *  # pylint: disable=W0614
from ...helpers import *  # pylint: disable=W0614
from ...module_system import *  # pylint: disable=W0614


def relation_slot_names():
    rel_start = ID_troops.trp_kingdom_heroes_including_player_begin
    rel_end = ID_troops.trp_heroes_end
    names = {}
    for id, name in varnames(ID_troops, 'trp_').items():
        if rel_start <= id < rel_end:
            names[id] = 'slot_relation.' + name[4:]
    return names


class Slots(object):
    quest_slots = slot_array('slot_quest_')

    site_slots = slot_array('slot_scene_')

    faction_slots = slot_array(
        'slot_faction_',
        types={
            module_constants.slot_faction_state: slot_enum('sfs_'),
            module_constants.slot_faction_ai_state: slot_enum('sfai_'),
        })

    party_template_slots = slot_array('slot_party_template_')

    party_slots = slot_array(
        'slot_party_',
        'slot_center_',
        'slot_town_',
        'slot_village_',
        'slot_castle_',
        types={
            module_constants.slot_party_type: slot_enum('spt_'),
            module_constants.slot_village_state: slot_enum('svs_'),
        })

    item_kind_slots = slot_array('slot_item_')

    troop_slots = slot_array(
        'slot_troop_',
        'slot_lord_',
        'slot_lady_',
        extra_keys=relation_slot_names(),
        types={
            module_constants.slot_troop_occupation: slot_enum('slto_', 'stl_'),
            module_constants.slot_lord_recruitment_argument: slot_enum('argument_'),
            module_constants.slot_troop_morality_state: slot_enum('tms_'),
            module_constants.slot_troop_morality_type: slot_enum('tmt_'),
            module_constants.slot_troop_personalityclash_state: slot_enum('pclash_'),
            module_constants.slot_troop_playerparty_history: slot_enum('pp_'),
            module_constants.slot_troop_mission_object: slot_enum('npc_mission_'),
            module_constants.slot_troop_mission_participation: slot_enum('mp_'),
            module_constants.slot_troop_recent_offense_type: slot_enum('tro_'),
            module_constants.slot_lord_reputation_type: slot_enum('lrep_'),
        })
