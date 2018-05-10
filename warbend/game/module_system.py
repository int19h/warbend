from __future__ import absolute_import, division, print_function

try:
    import module_info
except ImportError:
    import sys
    import traceback
    traceback.print_exc(file=sys.stderr)
    print('\nError loading Mount & Blade module system!',
          'Make sure that module_*.py files are in your PYTHONPATH.',
          'Module system for M&B Warband Native can be downloaded from:',
          'https://www.taleworlds.com/en/Games/Warband/Download',
          sep='\n', file=sys.stderr)
    sys.exit(1)

# pylint: disable=E0401
import ID_factions
import ID_info_pages
import ID_items
import ID_particle_systems
import ID_parties
import ID_party_templates
import ID_quests
import ID_scenes
import ID_tableau_materials
import ID_troops
import module_skills
import module_constants
import module_items
import module_troops


def global_variables():
    import os
    varfile = os.path.join(
        os.path.dirname(module_info.__file__),
        'variables.txt')
    with open(varfile, 'r') as f:
        return tuple(s.strip() for s in f)


global_variables = global_variables()
