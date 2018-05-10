# Derived from MnBSaveGameEditor's SaveGameStructure.cfg, which is in turn
# derived from the M&B modding wiki: http://mbmodwiki.ollclan.eu/Savegame

from __future__ import absolute_import, division, print_function

import sys

from ...data import *  # pylint: disable=W0614
from ..helpers import *  # pylint: disable=W0614
from ..module_system import *  # pylint: disable=W0614


def records(slots, dont_load_regular_troop_inventories=True):
    @record
    def header(self):
        assert parent(self) is root(self)
        self(magic_number=int32)
        self(game_version=int32)
        self(module_version=int32)
        self(savegame_name=pstr)
        self(player_name=pstr)
        self(player_level=int32)
        self(date=float32)

    @record
    def trigger(self):
        self(status=int32)
        self(check_timer=int64)
        self(delay_timer=int64)
        self(rearm_timer=int64)

    @record
    def simple_trigger(self):
        self(check_timer=int64)

    tableau_material_id = enum(int32, varnames(
        ID_tableau_materials, 'tableau_'))

    @record
    def note(self):
        self(text=pstr)
        self(value=int32)
        self(tableau_material_id=tableau_material_id)
        self(available=bool8)

    @record
    def quest(self):
        self(progression=int32)
        self(giver_troop_id=int32)
        self(number=int32)
        self(start_date=float32)
        self(title=pstr)
        self(text=pstr)
        self(giver=pstr)
        self(notes=array(note, 16))
        self(num_slots=int32)
        self(slots=slots.quest_slots(self))

    @record
    def info_page(self):
        self(notes=array(note, 16))

    @record
    def site(self):
        self(num_slots=int32)
        self(slots=slots.site_slots(self))

    @record
    def faction(self):
        game = root(self)
        self(num_slots=int32)
        self(slots=slots.faction_slots(self))
        self(relations=array(float32, game.num_factions, singular='relation'))
        self(name=pstr)
        self(renamed=bool8)
        self(color=uint32)
        self(_1=int32)
        self(notes=array(note, 16))

    @record
    def map_track(self):
        self(position_x=float32)
        self(position_y=float32)
        self(position_z=float32)
        self(rotation=float32)
        self(age=float32)
        self(flags=int32)

    @record
    def party_template(self):
        self(num_parties_created=int32)
        self(num_parties_destroyed=int32)
        self(num_parties_destroyed_by_player=int32)
        self(num_slots=int32)
        self(slots=slots.party_template_slots(self))

    @record
    def party_stack(self):
        self(troop_id=int32)
        self(num_troops=int32)
        self(num_wounded_troops=int32)
        self(flags=int32)

    particle_system_id = enum(int32, varnames(ID_particle_systems, 'psys_'))

    @record
    def party(self):
        game = root(self)
        self(valid=bool32)
        if not self.valid:
            return
        self(raw_id=int32)
        self(id=int32)
        self(party_id=pstr)
        self(name=pstr)
        self(flags=uint64)
        self(menu_id=int32)
        self(party_template_id=int32)
        self(faction_id=int32)
        self(personality=int32)
        self(default_behavior=int32)
        self(current_behavior=int32)
        self(default_behavior_object_id=int32)
        self(current_behavior_object_id=int32)
        self(initial_position_x=float32)
        self(initial_position_y=float32)
        self(target_position_x=float32)
        self(target_position_y=float32)
        self(position_x=float32)
        self(position_y=float32)
        self(position_z=float32)
        self(num_stacks=int32)
        self(stacks=array(party_stack, self.num_stacks))
        self(bearing=float32)
        self(renamed=bool8)
        self(extra_text=pstr)
        self(morale=float32)
        self(hunger=float32)
        self(_1=float32)
        self(patrol_radius=float32)
        self(initiative=float32)
        self(helpfulness=float32)
        self(label_visible=int32)
        self(bandit_attraction=float32)
        if 900 <= game.header.game_version < 1000 or game.header.game_version >= 1020:
            self(marshall=int32)
        self(ignore_player_timer=int64)
        self(banner_map_icon_id=int32)
        if game.header.game_version > 1136:
            self(extra_map_icon_id=int32)
            self(extra_map_icon_up_down_distance=float32)
            self(extra_map_icon_up_down_frequency=float32)
            self(extra_map_icon_rotate_frequency=float32)
            self(extra_map_icon_fade_frequency=float32)
        self(attached_to_party_id=int32)
        if game.header.game_version > 1161:
            self(_2=int32)
        self(is_attached=bool8)
        self(num_attached_party_ids=int32)
        self(attached_party_ids=array(
            int32, self.num_attached_party_ids, singular='party_id'))
        self(num_particle_system_ids=int32)
        self(particle_system_ids=array(
            particle_system_id,
            self.num_particle_system_ids,
            singular='particle_system_id'
        ))
        self(notes=array(note, 16))
        self(num_slots=int32)
        self(slots=slots.party_slots(self))

    @record
    def player_party_stack(self):
        game = root(self)
        party = game.parties[0]
        assert party.valid
        stack = party.stacks[self]
        troop = module_troops.troops[stack.troop_id]
        flags = troop[3]
        if flags & module_troops.tf_hero != 0:
            return

        self(experience=float32)
        self(num_upgradeable=int32)
        if selector(self) < 32:
            self(troop_dnas=array(int32, 32, singular='dna'))

    @record
    def map_event(self):
        self(valid=bool32)
        if not self.valid:
            return
        self(id=int32)
        self(text=pstr)
        self(type=int32)
        self(position_x=float32)
        self(position_y=float32)
        self(land_position_x=float32)
        self(land_position_y=float32)
        self(_1=float32)
        self(_2=float32)
        self(attacker_party_id=int32)
        self(defender_party_id=int32)
        self(battle_simulation_timer=int64)
        self(next_battle_simulation=float32)

    modifier = enum(uint8, varnames(module_items, 'imod_'))

    @record
    def item(self):
        self(item_kind_id=int32)
        self(hit_points=uint16)
        self(_1=uint8)
        self(modifier=modifier)

    @record
    def item_kind(self):
        self(num_slots=int32)
        self(slots=slots.item_kind_slots(self))

    @record
    def troop(self):
        self(num_slots=int32)
        self(slots=slots.troop_slots(self))
        self(attributes=array(int32, 4, singular='attribute',
                              keys=varnames(module_troops, 'ca_')))
        self(proficiencies=array(float32, 7, singular='proficiency',
                                 keys=varnames(module_troops, 'wpt_')))
        self(skills=bit_array(4, 48, singular='skill',
                              keys=varnames(module_skills, 'skl_')))
        self(notes=array(note, 16))
        self(flags=uint64)
        self(site_id_and_entry_no=int32)
        self(skill_points=int32)
        self(attribute_points=int32)
        self(proficiency_points=int32)
        self(level=int32)

        has_inventory = not dont_load_regular_troop_inventories or (
            self.flags & module_troops.tf_hero) != 0
        if has_inventory:
            self(gold=uint32)
            self(experience=int32)
            self(health=float32)
            self(faction_id=int32)
            self(inventory_items=array(item, 96))
            self(equipped_items=array(item, 10, keys=varnames(module_items, 'ek_')))
            self(face_keys=array(uint64, 4, singular='face_key'))
            self(renamed=bool8)
            if self.renamed:
                self(name=pstr)
                self(name_plural=pstr)
        self(class_no=int32)

    @record
    def game(self):
        self(header=header)
        self(game_time=uint64)
        self(random_seed=int32)
        self(save_mode=int32)
        if self.header.game_version > 1136:
            self(combat_difficulty=int32)
            self(combat_difficulty_friendlies=int32)
            self(reduce_combat_ai=int32)
            self(reduce_campaign_ai=int32)
            self(combat_speed=int32)
        self(date_timer=int64)
        self(hour=int32)
        self(day=int32)
        self(week=int32)
        self(month=int32)
        self(year=int32)
        self(_1=int32)
        self(global_cloud_amount=float32)
        self(global_haze_amount=float32)
        self(average_difficulty=float32)
        self(average_difficulty_period=float32)
        self(_2=pstr)
        self(_3=bool8)
        self(tutorial_flags=int32)
        self(default_prisoner_price=int32)
        self(encountered_party_1_id=int32)
        self(encountered_party_2_id=int32)
        self(current_menu_id=int32)
        self(current_site_id=int32)
        self(current_entry_no=int32)
        self(current_mission_template_id=int32)
        self(party_creation_min_random_value=int32)
        self(party_creation_max_random_value=int32)
        self(game_log=pstr)
        self(_4=array(int32, 6))
        self(_5=int64)
        self(rest_period=float32)
        self(rest_time_speed=int32)
        self(rest_is_int32eractive=int32)
        self(rest_remain_attackable=int32)
        self(class_names=array(pstr, 9, singular='class_name'))
        self(num_global_variables=int32)
        self(global_variables=array(
            int64, self.num_global_variables,
            singular='global_variable',
            keys={i: name for i, name in enumerate(global_variables)}
        ))
        self(num_triggers=int32)
        self(triggers=array(trigger, self.num_triggers))
        self(num_simple_triggers=int32)
        self(simple_triggers=array(simple_trigger, self.num_simple_triggers))
        self(num_quests=int32)
        self(quests=array(quest, self.num_quests, keys=varnames(ID_quests, 'qst_')))
        self(num_info_pages=int32)
        self(info_pages=array(info_page, self.num_info_pages,
                              keys=varnames(ID_info_pages, 'ip_')))
        self(num_sites=int32)
        self(sites=array(site, self.num_sites, keys=varnames(ID_scenes, 'scn_')))
        self(num_factions=int32)
        self(factions=array(
            faction, self.num_factions,
            keys=varnames(ID_factions, 'fac_'),
            groups=groups_from(ID_factions),
        ))
        self(num_map_tracks=int32)
        self(map_tracks=array(map_track, self.num_map_tracks))
        self(num_party_templates=int32)
        self(party_templates=array(party_template, self.num_party_templates,
                                   keys=varnames(ID_party_templates, 'pt_')))
        self(num_parties=int32)
        self(num_parties_created=int32)
        self(parties=array(party, self.num_parties, keys=varnames(ID_parties, 'p_')))
        self(player_party_stack_additional_info=array(
            player_party_stack, self.parties[0].num_stacks))
        self(num_map_events=int32)
        self(num_map_events_created=int32)
        self(map_events=array(map_event, self.num_map_events))
        self(num_troops=int32)
        self(troops=array(
            troop, self.num_troops,
            keys=varnames(ID_troops, 'trp_'),
            groups=groups_from(ID_troops),
        ))
        self(_6=array(int32, 42))
        self(num_item_kinds=int32)
        self(item_kind=array(
            item_kind, self.num_item_kinds,
            keys=varnames(ID_items, 'itm_'),
            groups=groups_from(ID_items),
        ))
        self(player_face_keys0=uint64)
        self(player_face_keys1=uint64)
        self(player_kill_count=int32)
        self(player_wounded_count=int32)
        self(player_own_troop_kill_count=int32)
        self(player_own_troop_wounded_count=int32)

    game
    return locals()
