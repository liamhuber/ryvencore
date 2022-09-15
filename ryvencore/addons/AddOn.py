"""
This module defines a simple addon system to extend node ryvencore's functionalities.
Some default addons are provided in the addons.default package, and additional addons
can be added by the user.

An addon
    - has a name, a version, a description
    - is session-specific
        - not per-flow
        - but you can of course implement per-flow functionality
    - manages its own state
        - in particular get_data() and set_data()
    - will be accessible by nodes as attribute (self.addon_name in the node)
        - during loading, addon access is blocked, so nodes should not access any
        addons in set_data(). This prevents inconsistent states. Nodes are loaded
        first, then the addons. Therefore, the addon should be sufficiently
        isolated and self-contained.

To define a custom addon you need to subclass the Addon class, and register you addon
with Session.register_addon(YourAddon()).
"""

from ryvencore.Base import Base


class AddOn(Base):
    name = ''
    version = ''
    description = ''

    def get_state(self) -> dict:
        """
        Return the state of the addon as JSON-compatible a dict.
        """
        return {}

    def set_state(self, state: dict):
        """
        Set the state of the addon from the dict generated in get_state().
        """
        pass
