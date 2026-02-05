
""" Openssl Elliptic Curve Parameters
Run ``openssl ecparam -list_curves`` to show all of the curve identifiers supported in OpenSSL.

import the ``charm.toolbox.eccurve`` module for the full listing from Charm.
"""

prime192v1 = 409
prime192v2 = 410
prime192v3 = 411
prime239v1 = 412
prime239v2 = 413
prime239v3 = 414
prime256v1 = 415

c2pnb163v1 = 684
c2pnb163v2 = 685
c2pnb163v3 = 686
c2pnb176v1 = 687
c2tnb191v1 = 688
c2tnb191v2 = 689
c2tnb191v3 = 690
c2onb191v4 = 691
c2onb191v5 = 692
c2pnb208w1 = 693

c2tnb239v1 = 694
c2tnb239v2 = 695
c2tnb239v3 = 696
c2onb239v4 = 697
c2onb239v5 = 698

c2pnb272w1 = 699
c2pnb304w1 = 700
c2tnb359v1 = 701
c2pnb368w1 = 702
c2tnb431r1 = 703

secp112r1 = 704
secp112r2 = 705
secp128r1 = 706
secp128r2 = 707
secp160k1 = 708
secp160r1 = 709
secp160r2 = 710
secp192k1 = 711
secp224k1 = 712
secp224r1 = 713
secp256k1 = 714
secp384r1 = 715
secp521r1 = 716
sect113r1 = 717
sect113r2 = 718
sect131r1 = 719
sect131r2 = 720
sect163k1 = 721
sect163r1 = 722
sect163r2 = 723
sect193r1 = 724
sect193r2 = 725
sect233k1 = 726
sect233r1 = 727
sect239k1 = 728
sect283k1 = 729
sect283r1 = 730
sect409k1 = 731
sect409r1 = 732
sect571k1 = 733
sect571r1 = 734

ecid_wtls1 = 735
ecid_wtls3 = 736
ecid_wtls4 = 737
ecid_wtls5 = 738
ecid_wtls6 = 739
ecid_wtls7 = 740
ecid_wtls8 = 741
ecid_wtls9 = 742
ecid_wtls10 = 743
ecid_wtls11 = 744
ecid_wtls12 = 745

curve_description = {  
  secp112r1 : 'SECG/WTLS curve over a 112 bit prime field',
  secp112r2 : 'SECG curve over a 112 bit prime field',
  secp128r1 : 'SECG curve over a 128 bit prime field',
  secp128r2 : 'SECG curve over a 128 bit prime field',
  secp160k1 : 'SECG curve over a 160 bit prime field',
  secp160r1 : 'SECG curve over a 160 bit prime field',
  secp160r2 : 'SECG/WTLS curve over a 160 bit prime field',
  secp192k1 : 'SECG curve over a 192 bit prime field',
  secp224k1 : 'SECG curve over a 224 bit prime field',
  secp224r1 : 'NIST/SECG curve over a 224 bit prime field',
  secp256k1 : 'SECG curve over a 256 bit prime field',
  secp384r1 : 'NIST/SECG curve over a 384 bit prime field',
  secp521r1 : 'NIST/SECG curve over a 521 bit prime field',
  prime192v1: 'NIST/X9.62/SECG curve over a 192 bit prime field',
  prime192v2: 'X9.62 curve over a 192 bit prime field',
  prime192v3: 'X9.62 curve over a 192 bit prime field',
  prime239v1: 'X9.62 curve over a 239 bit prime field',
  prime239v2: 'X9.62 curve over a 239 bit prime field',
  prime239v3: 'X9.62 curve over a 239 bit prime field',
  prime256v1: 'X9.62/SECG curve over a 256 bit prime field',
  sect113r1 : 'SECG curve over a 113 bit binary field',
  sect113r2 : 'SECG curve over a 113 bit binary field',
  sect131r1 : 'SECG/WTLS curve over a 131 bit binary field',
  sect131r2 : 'SECG curve over a 131 bit binary field',
  sect163k1 : 'NIST/SECG/WTLS curve over a 163 bit binary field',
  sect163r1 : 'SECG curve over a 163 bit binary field',
  sect163r2 : 'NIST/SECG curve over a 163 bit binary field',
  sect193r1 : 'SECG curve over a 193 bit binary field',
  sect193r2 : 'SECG curve over a 193 bit binary field',
  sect233k1 : 'NIST/SECG/WTLS curve over a 233 bit binary field',
  sect233r1 : 'NIST/SECG/WTLS curve over a 233 bit binary field',
  sect239k1 : 'SECG curve over a 239 bit binary field',
  sect283k1 : 'NIST/SECG curve over a 283 bit binary field',
  sect283r1 : 'NIST/SECG curve over a 283 bit binary field',
  sect409k1 : 'NIST/SECG curve over a 409 bit binary field',
  sect409r1 : 'NIST/SECG curve over a 409 bit binary field',
  sect571k1 : 'NIST/SECG curve over a 571 bit binary field',
  sect571r1 : 'NIST/SECG curve over a 571 bit binary field',
  c2pnb163v1: 'X9.62 curve over a 163 bit binary field',
  c2pnb163v2: 'X9.62 curve over a 163 bit binary field',
  c2pnb163v3: 'X9.62 curve over a 163 bit binary field',
  c2pnb176v1: 'X9.62 curve over a 176 bit binary field',
  c2tnb191v1: 'X9.62 curve over a 191 bit binary field',
  c2tnb191v2: 'X9.62 curve over a 191 bit binary field',
  c2tnb191v3: 'X9.62 curve over a 191 bit binary field',
  c2pnb208w1: 'X9.62 curve over a 208 bit binary field',
  c2tnb239v1: 'X9.62 curve over a 239 bit binary field',
  c2tnb239v2: 'X9.62 curve over a 239 bit binary field',
  c2tnb239v3: 'X9.62 curve over a 239 bit binary field',
  c2pnb272w1: 'X9.62 curve over a 272 bit binary field',
  c2pnb304w1: 'X9.62 curve over a 304 bit binary field',
  c2tnb359v1: 'X9.62 curve over a 359 bit binary field',
  c2pnb368w1: 'X9.62 curve over a 368 bit binary field',
  c2tnb431r1: 'X9.62 curve over a 431 bit binary field',
  ecid_wtls1: 'WTLS curve over a 113 bit binary field',
  ecid_wtls3: 'NIST/SECG/WTLS curve over a 163 bit binary field',
  ecid_wtls4: 'SECG curve over a 113 bit binary field',
  ecid_wtls5: 'X9.62 curve over a 163 bit binary field',
  ecid_wtls6: 'SECG/WTLS curve over a 112 bit prime field',
  ecid_wtls7: 'SECG/WTLS curve over a 160 bit prime field',
  ecid_wtls8: 'WTLS curve over a 112 bit prime field',
  ecid_wtls9: 'WTLS curve over a 160 bit prime field',
  ecid_wtls10:'NIST/SECG/WTLS curve over a 233 bit binary field',
  ecid_wtls11:'NIST/SECG/WTLS curve over a 233 bit binary field',
  ecid_wtls12:'WTLS curvs over a 224 bit prime field',
}
