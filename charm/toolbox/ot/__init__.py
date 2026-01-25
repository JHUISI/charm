"""
Oblivious Transfer (OT) Protocols for Charm

This module provides implementations of Oblivious Transfer protocols
for use with elliptic curve groups.

Available classes:
- SimpleOT: Simplest OT (Chou-Orlandi style) for 1-out-of-2 OT
- OTExtension: IKNP-style OT Extension for efficient many-OT execution
- DPF: Distributed Point Function based on GGM construction
- MPFSS: Multi-Point Function Secret Sharing using DPF
- SilentOT: Silent OT Extension using PCG (Boyle et al. Crypto 2019)
"""

from charm.toolbox.ot.base_ot import SimpleOT
from charm.toolbox.ot.ot_extension import OTExtension
from charm.toolbox.ot.dpf import DPF
from charm.toolbox.ot.mpfss import MPFSS
from charm.toolbox.ot.silent_ot import SilentOT

__all__ = ['SimpleOT', 'OTExtension', 'DPF', 'MPFSS', 'SilentOT']

