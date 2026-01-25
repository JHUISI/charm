.. _adapters:

Scheme Adapters
-----------------------------------------

Adapters are wrappers that transform or extend cryptographic schemes to provide
additional functionality. Common uses include:

* **Hybrid Encryption**: Combining asymmetric schemes with symmetric encryption
  to encrypt arbitrary-length messages
* **IBE-to-PKE Transforms**: Converting Identity-Based Encryption schemes into
  standard Public Key Encryption schemes
* **IBE-to-Signature Transforms**: Converting IBE schemes into signature schemes
* **Identity Hashing**: Allowing schemes that require group element identities
  to accept string identities instead

.. toctree::
   :maxdepth: 1

   charm/adapters/abenc_adapt_hybrid
   charm/adapters/dabenc_adapt_hybrid
   charm/adapters/ibenc_adapt_hybrid
   charm/adapters/ibenc_adapt_identityhash
   charm/adapters/kpabenc_adapt_hybrid
   charm/adapters/pkenc_adapt_bchk05
   charm/adapters/pkenc_adapt_chk04
   charm/adapters/pkenc_adapt_hybrid
   charm/adapters/pksig_adapt_naor01

