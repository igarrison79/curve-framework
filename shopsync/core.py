"""Core synchronization logic for ShopSync.

This module defines the :class:`ShopSync` class which coordinates inventory
synchronization. The actual integration with each marketplace is left as a
future implementation.
"""

from dataclasses import dataclass


@dataclass
class ShopSync:
    """Simple inventory synchronization engine.

    Attributes
    ----------
    system_of_record:
        Name of the marketplace that should be treated as the source of truth
        for inventory counts.
    """

    system_of_record: str

    def sync_inventory(self) -> str:
        """Placeholder method representing an inventory sync.

        Returns
        -------
        str
            Description of the sync process.
        """

        return f"Syncing inventory using {self.system_of_record} as system of record"
