"""Regression tests adapted from the supplied bugs/ share-mismatch reproducers."""
import pytest

from charm.schemes.abenc import (
    abenc_bsw07,
    abenc_lsw08,
    abenc_maabe_yj14,
    abenc_tbpre_lww14,
    abenc_unmcpabe_yahk14,
    abenc_waters09,
    ac17,
)
from charm.toolbox.pairinggroup import GT, PairingGroup


def test_tbpre_lww14_share_mismatch_rejected():
    group = PairingGroup("SS512")
    tbpre = abenc_tbpre_lww14.TBPRE(group)
    attributes = ["A", "B", "C", "D"]
    MK, PK, s, H = tbpre.setup(attributes)

    alice = {"id": "alice"}
    alice["sku"], pubuser = tbpre.registerUser(PK, H)
    keyTime = {"year": "2026"}
    for attr in attributes:
        tbpre.keygen(MK, PK, H, s, alice, pubuser, attr, keyTime)

    orig_msg = group.random(GT)
    policy = [["A"]]
    currentDate = {"year": "2026", "month": "8", "day": "24"}
    CT = tbpre.encrypt(PK, policy, orig_msg)
    CT_t = tbpre.reencrypt(PK, H, s, CT, currentDate)

    # Reject changed term sizes before truncated integer division can corrupt plaintext.
    CT_t["A"] = [["A", "B", "C", "D"]]
    with pytest.raises(ValueError, match="Policy terms"):
        tbpre.decrypt(CT_t, alice)


def test_bsw07_share_mismatch_rejected(capsys):
    group = PairingGroup("BN254")
    scheme = abenc_bsw07.CPabe_BSW07(group)
    pk, mk = scheme.setup()

    sk_attacker = scheme.keygen(pk, mk, ["A", "B", "C", "D"])
    orig_msg = group.random(GT)
    ct = scheme.encrypt(pk, orig_msg, "A")
    ct["policy"] = "A and B and C and D"

    with pytest.raises(ValueError, match="Policy leaves"):
        scheme.decrypt(pk, sk_attacker, ct)
    assert capsys.readouterr().out == ''


# Mismatched share sets must fail explicitly before pairing operations.


def test_mismatching_ac17_rejected():
    group = PairingGroup("BN254")
    scheme = ac17.AC17CPABE(group, 2)
    pk, mk = scheme.setup()
    sk = scheme.keygen(pk, mk, ["A", "B", "C", "D"])

    orig_msg = group.random(GT)
    ct = scheme.encrypt(pk, orig_msg, "A")
    ct["policy"] = scheme.util.createPolicy("A and B and C and D")

    with pytest.raises(ValueError, match="Policy leaves"):
        scheme.decrypt(pk, ct, sk)


def test_mismatching_lws08_rejected():
    group = PairingGroup("BN254")
    scheme = abenc_lsw08.KPabe(group)
    pk, mk = scheme.setup()
    key = scheme.keygen(pk, mk, "A")
    orig_msg = group.random(GT)
    ct = scheme.encrypt(pk, orig_msg, ["A", "B", "C", "D"])
    key["policy"] = "A and B and C and D"

    with pytest.raises(ValueError, match="Policy leaves"):
        scheme.decrypt(ct, key)


def test_mismatching_waters09_rejected():
    group = PairingGroup("BN254")
    scheme = abenc_waters09.CPabe09(group)
    msk, pk = scheme.setup()
    sk = scheme.keygen(pk, msk, ["A", "B", "C", "D"])
    orig_msg = group.random(GT)
    ct = scheme.encrypt(pk, orig_msg, "A")
    ct["policy"] = "A and B and C and D"

    with pytest.raises(ValueError, match="Policy leaves"):
        scheme.decrypt(pk, sk, ct)


def test_mismatching_yahk14_rejected():
    group = PairingGroup("SS512")
    scheme = abenc_unmcpabe_yahk14.CPABE_YAHK14(group)
    pp, mk = scheme.setup()
    sk = scheme.keygen(pp, mk, ["1", "2", "3", "4"])
    orig_msg = group.random(GT)
    ct = scheme.encrypt(pp, orig_msg, "1")
    ct["Policy"] = "1 and 2 and 3 and 4"

    with pytest.raises(ValueError, match="Policy leaves"):
        scheme.decrypt(pp, sk, ct)


def test_mismatching_yj14_rejected():
    group = PairingGroup("SS512")
    scheme = abenc_maabe_yj14.MAABE(group)
    GPP, _ = scheme.setup()
    authorities = {}
    attributes = ["A", "B", "C", "D"]
    scheme.setupAuthority(GPP, "authority1", attributes, authorities)
    users = {}
    alice = {"id": "alice", "authoritySecretKeys": {}, "keys": None}
    alice["keys"], users[alice["id"]] = scheme.registerUser(GPP)
    for attr in attributes:
        scheme.keygen(
            GPP,
            authorities["authority1"],
            attr,
            users[alice["id"]],
            alice["authoritySecretKeys"],
        )

    orig_msg = group.random(GT)
    ct = scheme.encrypt(GPP, "A", orig_msg, authorities["authority1"])
    ct["policy"] = "A and B and C and D"

    with pytest.raises(ValueError, match="Policy leaves"):
        scheme.decrypt(GPP, ct, alice)
