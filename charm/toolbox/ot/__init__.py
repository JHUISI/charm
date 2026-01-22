"""
Oblivious Transfer (OT) Protocols for Charm

This module provides implementations of Oblivious Transfer protocols
for use with elliptic curve groups.

Available classes:
- SimpleOT: Simplest OT (Chou-Orlandi style) for 1-out-of-2 OT
- OTExtension: IKNP-style OT Extension for efficient many-OT execution
"""

from charm.toolbox.ot.base_ot import SimpleOT
from charm.toolbox.ot.ot_extension import OTExtension

__all__ = ['SimpleOT', 'OTExtension']

