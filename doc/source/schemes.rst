.. _schemes:

Implemented Schemes
-----------------------------------------

.. sectionauthor:: J. Ayo Akinyele

This section contains documentation for all cryptographic schemes implemented in Charm.
Schemes are organized by type: attribute-based encryption (ABE), public-key encryption,
public-key signatures, identity-based encryption, threshold signatures, and more.
Each scheme includes implementation details, security assumptions, and usage examples.

Threshold Signatures
^^^^^^^^^^^^^^^^^^^^

Charm provides three production-ready threshold ECDSA implementations for MPC-based
distributed signing. These enable *t-of-n* signing where any *t* parties can
collaboratively produce a valid signature without reconstructing the private key.

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Scheme
     - Description
     - Reference
   * - **GG18**
     - Classic Paillier-based threshold ECDSA (4-round interactive signing)
     - `Gennaro & Goldfeder 2018 <https://eprint.iacr.org/2019/114.pdf>`_
   * - **CGGMP21**
     - UC-secure with identifiable aborts and presigning
     - `Canetti et al. 2021 <https://eprint.iacr.org/2021/060>`_
   * - **DKLS23**
     - OT-based MtA with non-interactive presigning
     - `Doerner et al. 2023 <https://eprint.iacr.org/2023/765>`_

All schemes support **secp256k1** (Bitcoin, XRPL) and other elliptic curves.
See :doc:`threshold` for detailed documentation, API reference, and usage examples.

**Quick Example (GG18):**

.. code-block:: python

    from charm.toolbox.ecgroup import ECGroup
    from charm.toolbox.eccurve import secp256k1
    from charm.schemes.threshold import GG18

    group = ECGroup(secp256k1)
    gg18 = GG18(group, threshold=2, num_parties=3)
    key_shares, public_key = gg18.keygen()
    signature = gg18.sign(key_shares[:2], b"message")
    assert gg18.verify(public_key, b"message", signature)

Other Schemes
^^^^^^^^^^^^^

.. begin_auto_scheme_list
.. toctree::
   :maxdepth: 1

   charm/schemes/aggrsign_bls
   charm/schemes/aggrsign_MuSig
   charm/schemes/blindsig_ps16
   charm/schemes/chamhash_adm05
   charm/schemes/chamhash_rsa_hw09
   charm/schemes/encap_bchk05
   charm/schemes/joye_scheme
   charm/schemes/lem_scheme
   charm/schemes/pk_vrf
   charm/schemes/pre_mg07
   charm/schemes/protocol_a01
   charm/schemes/protocol_ao00
   charm/schemes/protocol_cns07
   charm/schemes/protocol_schnorr91
   charm/schemes/sigma1
   charm/schemes/sigma2
   charm/schemes/sigma3
   charm/schemes/abenc/abenc_accountability_jyjxgd20
   charm/schemes/abenc/abenc_bsw07
   charm/schemes/abenc/abenc_ca_cpabe_ar17
   charm/schemes/abenc/abenc_dacmacs_yj14
   charm/schemes/abenc/abenc_lsw08
   charm/schemes/abenc/abenc_maabe_rw15
   charm/schemes/abenc/abenc_maabe_yj14
   charm/schemes/abenc/abenc_tbpre_lww14
   charm/schemes/abenc/abenc_unmcpabe_yahk14
   charm/schemes/abenc/abenc_waters09
   charm/schemes/abenc/abenc_yct14
   charm/schemes/abenc/abenc_yllc15
   charm/schemes/abenc/ac17
   charm/schemes/abenc/bsw07
   charm/schemes/abenc/cgw15
   charm/schemes/abenc/dabe_aw11
   charm/schemes/abenc/dfa_fe12
   charm/schemes/abenc/pk_hve08
   charm/schemes/abenc/waters11
   charm/schemes/pkenc/pkenc_cs98
   charm/schemes/pkenc/pkenc_elgamal85
   charm/schemes/pkenc/pkenc_gm82
   charm/schemes/pkenc/pkenc_paillier99
   charm/schemes/pkenc/pkenc_rabin
   charm/schemes/pkenc/pkenc_rsa
   charm/schemes/pksig/pksig_bls04
   charm/schemes/pksig/pksig_boyen
   charm/schemes/pksig/pksig_chch
   charm/schemes/pksig/pksig_chp
   charm/schemes/pksig/pksig_cl03
   charm/schemes/pksig/pksig_cl04
   charm/schemes/pksig/pksig_cllww12_z
   charm/schemes/pksig/pksig_CW13_z
   charm/schemes/pksig/pksig_cyh
   charm/schemes/pksig/pksig_dsa
   charm/schemes/pksig/pksig_ecdsa
   charm/schemes/pksig/pksig_hess
   charm/schemes/pksig/pksig_hw
   charm/schemes/pksig/pksig_lamport
   charm/schemes/pksig/pksig_ps01
   charm/schemes/pksig/pksig_ps02
   charm/schemes/pksig/pksig_ps03
   charm/schemes/pksig/pksig_rsa_hw09
   charm/schemes/pksig/pksig_schnorr91
   charm/schemes/pksig/pksig_waters
   charm/schemes/pksig/pksig_waters05
   charm/schemes/pksig/pksig_waters09

.. end_auto_scheme_list

