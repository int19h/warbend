from __future__ import absolute_import, division, print_function

import operator

from ....data import *  # pylint: disable=W0614
from ...helpers import *  # pylint: disable=W0614
from ...module_system import *  # pylint: disable=W0614

c = module_constants


def relation_slot_names():
    rel_start = ID_troops.trp_kingdom_heroes_including_player_begin
    rel_end = ID_troops.trp_heroes_end
    names = {}
    for id, name in varnames(ID_troops, 'trp_').items():
        if rel_start <= id < rel_end:
            names[id] = 'slot_relation.' + name[4:]
    return names


class Slots(object):
    faction_id = id_ref(int64, lambda game: game.factions, checked=False)

    troop_id = id_ref(int64, lambda game: game.troops, checked=False)

    party_template_id = id_ref(int64, lambda game: game.party_templates, checked=False)

    item_kind_id = id_ref(int64, lambda game: game.item_kinds, checked=False)

    quest_id = id_ref(int64, lambda game: game.quests, checked=False)

    # Parties can be created and destroyed dynamically, so it's possible
    # for a party_id to refer to a party that no longer exists.
    party_id = id_ref(int64, lambda game: game.parties, checked=False)

    quest_slots = slot_array(
        'slot_quest_',
        types={
            c.slot_quest_target_center: party_id,
            c.slot_quest_target_troop: troop_id,
            c.slot_quest_target_faction: faction_id,
            c.slot_quest_object_troop: troop_id,
            c.slot_quest_giver_troop: troop_id,
            c.slot_quest_object_center: party_id,
            c.slot_quest_target_party: party_id,
            c.slot_quest_target_party_template: party_template_id,
            c.slot_quest_giver_center: party_id,
            c.slot_quest_target_item: item_kind_id,
            c.slot_quest_object_faction: faction_id,
        })

    site_slots = slot_array('slot_scene_')

    faction_slots = slot_array(
        'slot_faction_',
        types={
            c.slot_faction_state: slot_enum('sfs_'),
            c.slot_faction_ai_state: slot_enum('sfai_'),
            c.slot_faction_marshall: troop_id,
            c.slot_faction_leader: troop_id,
            c.slot_faction_quick_battle_tier_1_infantry: troop_id,
            c.slot_faction_quick_battle_tier_2_infantry: troop_id,
            c.slot_faction_quick_battle_tier_1_archer: troop_id,
            c.slot_faction_quick_battle_tier_2_archer: troop_id,
            c.slot_faction_quick_battle_tier_1_cavalry: troop_id,
            c.slot_faction_quick_battle_tier_2_cavalry: troop_id,
            c.slot_faction_tier_1_troop: troop_id,
            c.slot_faction_tier_2_troop: troop_id,
            c.slot_faction_tier_3_troop: troop_id,
            c.slot_faction_tier_4_troop: troop_id,
            c.slot_faction_tier_5_troop: troop_id,
            c.slot_faction_deserter_troop: troop_id,
            c.slot_faction_guard_troop: troop_id,
            c.slot_faction_messenger_troop: troop_id,
            c.slot_faction_prison_guard_troop: troop_id,
            c.slot_faction_castle_guard_troop: troop_id,
            c.slot_faction_town_walker_male_troop: troop_id,
            c.slot_faction_town_walker_female_troop: troop_id,
            c.slot_faction_village_walker_male_troop: troop_id,
            c.slot_faction_village_walker_female_troop: troop_id,
            c.slot_faction_town_spy_male_troop: troop_id,
            c.slot_faction_town_spy_female_troop: troop_id,
            c.slot_faction_last_attacked_center: party_id,

        })

    party_template_slots = slot_array('slot_party_template_')

    party_slots = slot_array(
        'slot_party_',
        'slot_center_',
        'slot_town_',
        'slot_village_',
        'slot_castle_',
        types={
            c.slot_party_type: slot_enum('spt_'),
            c.slot_village_state: slot_enum('svs_'),
            c.slot_town_lord: troop_id,
            c.slot_town_tavernkeeper: troop_id,
            c.slot_town_weaponsmith: troop_id,
            c.slot_town_armorer: troop_id,
            c.slot_town_merchant: troop_id,
            c.slot_town_horse_merchant: troop_id,
            c.slot_town_elder: troop_id,
            c.slot_center_last_taken_by_troop: troop_id,
            c.slot_party_commander_party: party_id,
            c.slot_village_raided_by: troop_id,
            c.slot_center_is_besieged_by: troop_id,
            c.slot_town_reinforcement_party_template: party_template_id,
            c.slot_center_original_faction: faction_id,
            c.slot_center_ex_faction: faction_id,
            c.slot_town_village_product: item_kind_id,
            c.slot_center_npc_volunteer_troop_type: troop_id,
            c.slot_center_mercenary_troop_type: troop_id,
            c.slot_center_volunteer_troop_type: troop_id,
            c.slot_center_ransom_broker: troop_id,
            c.slot_center_tavern_traveler: troop_id,
            c.slot_center_traveler_info_faction: troop_id,
            c.slot_center_tavern_bookseller: troop_id,
            c.slot_center_tavern_minstrel: troop_id,
            c.slot_village_bound_center: party_id,
            c.slot_village_market_town: party_id,
            c.slot_village_farmer_party: party_id,
            c.slot_party_home_center: party_id,
            c.slot_party_last_traded_center: party_id,
            c.slot_center_faction_when_oath_renounced: faction_id,
            c.slot_center_walker_0_troop: troop_id,
            c.slot_center_walker_1_troop: troop_id,
            c.slot_center_walker_2_troop: troop_id,
            c.slot_center_walker_3_troop: troop_id,
            c.slot_center_walker_4_troop: troop_id,
            c.slot_center_walker_5_troop: troop_id,
            c.slot_center_walker_6_troop: troop_id,
            c.slot_center_walker_7_troop: troop_id,
            c.slot_center_walker_8_troop: troop_id,
            c.slot_center_walker_9_troop: troop_id,
            c.slot_town_trade_route_1: party_id,
            c.slot_town_trade_route_2: party_id,
            c.slot_town_trade_route_3: party_id,
            c.slot_town_trade_route_4: party_id,
            c.slot_town_trade_route_5: party_id,
            c.slot_town_trade_route_6: party_id,
            c.slot_town_trade_route_7: party_id,
            c.slot_town_trade_route_8: party_id,
            c.slot_town_trade_route_9: party_id,
            c.slot_town_trade_route_10: party_id,
            c.slot_town_trade_route_11: party_id,
            c.slot_town_trade_route_12: party_id,
            c.slot_town_trade_route_13: party_id,
            c.slot_town_trade_route_14: party_id,
            c.slot_town_trade_route_15: party_id,
            c.slot_party_following_orders_of_troop: troop_id,
        })

    item_kind_slots = slot_array(
        'slot_item_',
        types={
            c.slot_item_primary_raw_material: item_kind_id,
            c.slot_item_secondary_raw_material: item_kind_id,
            c.slot_item_is_raw_material_only_for: item_kind_id,
        })

    real_troop_slots = slot_array(
        'slot_troop_',
        'slot_lord_',
        'slot_lady_',
        exclude_prefixes=('slot_troop_trainer',),
        extra_keys=relation_slot_names(),
        types={
            c.slot_troop_occupation: slot_enum('slto_', 'stl_'),
            c.slot_lord_recruitment_argument: slot_enum('argument_'),
            c.slot_troop_kingsupport_argument: slot_enum('argument_'),
            c.slot_troop_morality_state: slot_enum('tms_'),
            c.slot_troop_morality_type: slot_enum('tmt_'),
            c.slot_troop_personalityclash_state: slot_enum('pclash_'),
            c.slot_troop_playerparty_history: slot_enum('pp_'),
            c.slot_troop_mission_object: slot_enum('npc_mission_'),
            c.slot_troop_mission_participation: slot_enum('mp_'),
            c.slot_troop_recent_offense_type: slot_enum('tro_'),
            c.slot_lord_reputation_type: slot_enum('lrep_'),
            c.slot_troop_party_template: party_template_id,
            c.slot_troop_prisoner_of_party: party_id,
            c.slot_troop_cur_center: party_id,
            c.slot_troop_original_faction: faction_id,
            c.slot_troop_last_quest: quest_id,
            c.slot_troop_spouse: troop_id,
            c.slot_troop_father: troop_id,
            c.slot_troop_mother: troop_id,
            c.slot_troop_guardian: troop_id,
            c.slot_troop_betrothed: troop_id,
            c.slot_troop_love_interest_1: troop_id,
            c.slot_troop_love_interest_2: troop_id,
            c.slot_troop_love_interest_3: troop_id,
            c.slot_lady_last_suitor: troop_id,
            c.slot_troop_promised_fief: party_id,
            c.slot_lord_recruitment_candidate: troop_id,
            c.slot_troop_first_encountered: party_id,
            c.slot_troop_home: party_id,
            c.slot_troop_town_with_contacts: party_id,
        })

    # Some troops are dummy entries, with their slots used to simulate arrays.
    # For those array troops, the meaning of slots differs from regular troops.
    # This mapping captures the "array element" type for each of them, which
    # then becomes the type of every slot they have.
    array_troops = {
        ID_troops.trp_banner_background_color_array: int64,
        ID_troops.trp_log_array_entry_type: slot_enum('logent_'),
        ID_troops.trp_log_array_entry_time: int64,
        ID_troops.trp_log_array_actor: int64,
        ID_troops.trp_log_array_center_object: party_id,
        ID_troops.trp_log_array_center_object_lord: troop_id,
        ID_troops.trp_log_array_center_object_faction: faction_id,
        ID_troops.trp_log_array_troop_object: troop_id,
        ID_troops.trp_log_array_troop_object_faction: faction_id,
        ID_troops.trp_log_array_faction_object: faction_id,
        ID_troops.trp_temp_array_a: int64,
        ID_troops.trp_temp_array_b: int64,
        ID_troops.trp_temp_array_c: int64,
        ID_troops.trp_stack_selection_amounts: int64,
        ID_troops.trp_stack_selection_ids: int64,
        ID_troops.trp_notification_menu_types: int64,
        ID_troops.trp_notification_menu_var1: int64,
        ID_troops.trp_notification_menu_var2: int64,
    }

    @staticmethod
    def troop_slots(troop):
        index = operator.index(troop)
        try:
            t = Slots.array_troops[index]
        except KeyError:
            return Slots.real_troop_slots(troop)
        else:
            return array(t, troop.num_slots)
