Changes in v0.50
=======================

This release includes new cryptographic schemes, platform improvements, and bug fixes.

New Schemes
^^^^^^^^^^^

- Added implementation of private aggregate of time series data by Marc Joye et al.
- Added Abe's blind signature scheme [AO00, A01]
- Added hibenc_lew11.py
- Added Goldwasser-Micali pkenc scheme
- Added Leontiadis-Elkhyiaoui-Molva scheme
- Added four more ABE schemes
- Re-added Time-based proxy re-encryption scheme implementation for py3
- Added non-monotonic CP-ABE scheme by Yamada, Attrapadung, Hanaoka, Kunihiro
- Added BBS98 proxy re-encryption scheme
- Added implementation of AFGH06 scheme
- Added first NAL16 scheme
- Added NAL16b (CCA_21 version of NAL16a)
- Added scheme from Rouselakis and Waters (maabe_rw12.py)
- Ciphertext-policy ABE schemes implemented under asymmetric pairing groups (any policy represented as a monotone span program can be handled)

Proxy Re-Encryption
^^^^^^^^^^^^^^^^^^^

- Interface for Proxy Re-Encryption schemes (charm.toolbox.PREnc)
- Adapted BBS98 to PREnc interface

Core Improvements
^^^^^^^^^^^^^^^^^

- Error handling updates to base modules
- CL03: length of e is now verified, verifyCommit() and header added
- SHA1(m_i) for doctest (verifyCommit) added
- Added hash support to wrapped pbc ecc elements (pairingmodule.c)
- Added support for uncompressed curves elements (de)serialization
- Improved arguments management in (de)serialize methods of the c pairingmodule
- Improved error management in deserialize c pairingmodule
- Improved error management in pairing product routine of pairinggroup.c
- Improved error handling for initialize and initPP, new preproc attribute
- Changed hash function from sha1 to sha256 everywhere appropriate
- Simplified encode/decode of messages in ECGroups (squashed bugs related to BN_bin2bn/BN_bn2bin)
- Added py2.7 compatibility for pairing group serialize/deserialize

Platform Support
^^^^^^^^^^^^^^^^

- Updated configure.sh to support ARM (android, raspberry pi, include armv7l support)
- Added support for Mac OS X 10.11+
- Updated to install file for windows and nsis script
- Added Dockerfile to document installation process
- Fixed compilation errors with OpenSSL 1.1.0 caused by API change

Bug Fixes
^^^^^^^^^

- Fixed typo in protocol_a00.py and protocol_ao00.py
- Fix configure.sh: detect python better (thanks to Neal H. Walfield)
- Fix decrypt error when plaintext=0 for Paillier scheme (closes #97)
- Update libtomcrypt headers to v1.17
- Renamed sha1 to sha2 and update version to v0.5

Documentation
^^^^^^^^^^^^^

- Added documentation

Contributors
^^^^^^^^^^^^

Scheme contributions, bug fixes and/or various improvements from:
@adelapie, @leontiad, @nikosft, @0xwille, @artjomb, @cygnusv, @lferr,
@denniss17, @locksmithone, @leafac, @ElectroSuccess, @sagrawal87.

Thanks to all!
