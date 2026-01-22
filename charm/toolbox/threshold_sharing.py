"""
Threshold Secret Sharing for DKLS23 and Threshold ECDSA

This module extends Shamir secret sharing for threshold ECDSA requirements,
providing Feldman VSS, Pedersen commitments, and EC group element support.
"""

from charm.toolbox.ecgroup import ECGroup, ZR, G
from charm.toolbox.eccurve import secp256k1
from charm.toolbox.secretshare import SecretShare


class ThresholdSharing:
    """
    Enhanced secret sharing for threshold ECDSA
    
    Supports Feldman VSS and operations on EC groups
    
    >>> from charm.toolbox.eccurve import secp256k1
    >>> group = ECGroup(secp256k1)
    >>> ts = ThresholdSharing(group)
    >>> g = group.random(G)
    >>> secret = group.random(ZR)
    >>> shares, commitments = ts.share_with_verification(secret, g, threshold=2, num_parties=3)
    >>> ts.verify_share(1, shares[1], commitments, g)
    True
    >>> ts.verify_share(2, shares[2], commitments, g)
    True
    >>> ts.verify_share(3, shares[3], commitments, g)
    True
    >>> recovered = ts.reconstruct({1: shares[1], 2: shares[2]}, threshold=2)
    >>> secret == recovered
    True
    """
    
    def __init__(self, groupObj):
        """
        Initialize threshold sharing with an EC group
        
        Args:
            groupObj: An ECGroup instance (e.g., ECGroup(secp256k1))
        """
        self.group = groupObj
        self.order = groupObj.order()
        
    def _eval_polynomial(self, coeffs, x):
        """
        Evaluate polynomial at point x
        
        Args:
            coeffs: List of coefficients [a_0, a_1, ..., a_{t-1}]
            x: Point to evaluate at (ZR element or int)
        
        Returns:
            Polynomial value at x
        """
        if isinstance(x, int):
            x = self.group.init(ZR, x)
        
        result = self.group.init(ZR, 0)
        x_power = self.group.init(ZR, 1)
        
        for coeff in coeffs:
            result = result + (coeff * x_power)
            x_power = x_power * x
            
        return result
    
    def share(self, secret, threshold, num_parties):
        """
        Basic Shamir secret sharing
        
        Args:
            secret: The secret to share (ZR element)
            threshold: Minimum number of shares needed to reconstruct (t)
            num_parties: Total number of parties (n)
            
        Returns:
            Dictionary mapping party_id (1 to n) to share values
            
        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> ts = ThresholdSharing(group)
        >>> secret = group.random(ZR)
        >>> shares = ts.share(secret, threshold=2, num_parties=4)
        >>> len(shares) == 4
        True
        >>> recovered = ts.reconstruct({1: shares[1], 3: shares[3]}, threshold=2)
        >>> secret == recovered
        True
        """
        if threshold > num_parties:
            raise ValueError("threshold cannot exceed num_parties")
        if threshold < 1:
            raise ValueError("threshold must be at least 1")
            
        # Generate random polynomial coefficients: a_0 = secret, a_1...a_{t-1} random
        coeffs = [secret]
        for _ in range(threshold - 1):
            coeffs.append(self.group.random(ZR))
            
        # Evaluate polynomial at points 1, 2, ..., n
        shares = {}
        for i in range(1, num_parties + 1):
            shares[i] = self._eval_polynomial(coeffs, i)
            
        return shares
    
    def share_with_verification(self, secret, generator, threshold, num_parties):
        """
        Feldman VSS - shares with public commitments for verification
        
        Creates shares using Shamir's scheme and publishes commitments
        C_j = g^{a_j} for each coefficient a_j, allowing verification
        without revealing the secret.
        
        Args:
            secret: The secret to share (ZR element)
            generator: Generator point g in the EC group (G element)
            threshold: Minimum shares needed to reconstruct
            num_parties: Total number of parties
            
        Returns:
            Tuple of (shares_dict, commitments_list)
            - shares_dict: {party_id: share_value}
            - commitments_list: [C_0, C_1, ..., C_{t-1}] where C_j = g^{a_j}
            
        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> ts = ThresholdSharing(group)
        >>> g = group.random(G)
        >>> secret = group.random(ZR)
        >>> shares, comms = ts.share_with_verification(secret, g, 2, 3)
        >>> all(ts.verify_share(i, shares[i], comms, g) for i in range(1, 4))
        True
        """
        if threshold > num_parties:
            raise ValueError("threshold cannot exceed num_parties")
        if threshold < 1:
            raise ValueError("threshold must be at least 1")
            
        # Generate polynomial coefficients
        coeffs = [secret]
        for _ in range(threshold - 1):
            coeffs.append(self.group.random(ZR))
            
        # Compute Feldman commitments: C_j = g^{a_j}
        commitments = [generator ** coeff for coeff in coeffs]
        
        # Generate shares
        shares = {}
        for i in range(1, num_parties + 1):
            shares[i] = self._eval_polynomial(coeffs, i)
            
        return shares, commitments
    
    def verify_share(self, party_id, share, commitments, generator):
        """
        Verify a share against Feldman commitments
        
        Checks that g^{share} == prod_{j=0}^{t-1} C_j^{i^j}
        
        Args:
            party_id: The party's identifier (1 to n)
            share: The share value to verify (ZR element)
            commitments: List of Feldman commitments [C_0, ..., C_{t-1}]
            generator: Generator point g used in commitments
            
        Returns:
            True if share is valid, False otherwise
        """
        # Compute g^{share}
        lhs = generator ** share
        
        # Compute prod_{j=0}^{t-1} C_j^{i^j}
        rhs = commitments[0]  # C_0^{i^0} = C_0
        i_power = self.group.init(ZR, party_id)
        
        for j in range(1, len(commitments)):
            rhs = rhs * (commitments[j] ** i_power)
            i_power = i_power * self.group.init(ZR, party_id)
            
        return lhs == rhs

    def reconstruct(self, shares, threshold):
        """
        Reconstruct secret from threshold shares using Lagrange interpolation

        Args:
            shares: Dictionary {party_id: share_value} with at least threshold entries
            threshold: The threshold used when sharing

        Returns:
            The reconstructed secret

        Raises:
            ValueError: If fewer than threshold shares provided

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> ts = ThresholdSharing(group)
        >>> secret = group.random(ZR)
        >>> shares = ts.share(secret, threshold=3, num_parties=5)
        >>> recovered = ts.reconstruct({1: shares[1], 2: shares[2], 4: shares[4]}, 3)
        >>> secret == recovered
        True
        """
        if len(shares) < threshold:
            raise ValueError(f"Need at least {threshold} shares, got {len(shares)}")

        party_ids = list(shares.keys())

        # Compute secret = sum of (share_i * lagrange_coeff_i) at x=0
        secret = self.group.init(ZR, 0)
        for i in party_ids:
            coeff = self.lagrange_coefficient(party_ids, i, x=0)
            secret = secret + (shares[i] * coeff)

        return secret

    def lagrange_coefficient(self, party_ids, i, x=0):
        """
        Compute Lagrange coefficient for party i at point x

        L_i(x) = prod_{j != i} (x - j) / (i - j)

        Args:
            party_ids: List of party identifiers in the reconstruction set
            i: The party for which to compute the coefficient
            x: The evaluation point (default 0 for secret recovery)

        Returns:
            The Lagrange coefficient as a ZR element

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> ts = ThresholdSharing(group)
        >>> coeff = ts.lagrange_coefficient([1, 2, 3], 1, x=0)
        >>> # L_1(0) = (0-2)(0-3) / (1-2)(1-3) = 6/2 = 3
        """
        if isinstance(x, int):
            x = self.group.init(ZR, x)
        i_zr = self.group.init(ZR, i)

        result = self.group.init(ZR, 1)
        for j in party_ids:
            if j != i:
                j_zr = self.group.init(ZR, j)
                numerator = x - j_zr
                denominator = i_zr - j_zr
                result = result * numerator * (denominator ** -1)

        return result

    def add_shares(self, shares1, shares2):
        """
        Add two sets of shares (for additive share combination)

        Useful for distributed key generation and refreshing.

        Args:
            shares1: First dictionary of shares {party_id: share}
            shares2: Second dictionary of shares {party_id: share}

        Returns:
            Dictionary of combined shares

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> ts = ThresholdSharing(group)
        >>> s1, s2 = group.random(ZR), group.random(ZR)
        >>> shares1 = ts.share(s1, 2, 3)
        >>> shares2 = ts.share(s2, 2, 3)
        >>> combined = ts.add_shares(shares1, shares2)
        >>> recovered = ts.reconstruct({1: combined[1], 2: combined[2]}, 2)
        >>> recovered == s1 + s2
        True
        """
        if set(shares1.keys()) != set(shares2.keys()):
            raise ValueError("Share sets must have same party IDs")

        combined = {}
        for party_id in shares1.keys():
            combined[party_id] = shares1[party_id] + shares2[party_id]

        return combined

    def refresh_shares(self, shares, threshold):
        """
        Refresh shares for proactive security

        Generates new shares of zero and adds them to existing shares.
        The new shares reconstruct to the same secret but are unlinkable
        to the old shares.

        Args:
            shares: Dictionary of current shares {party_id: share}
            threshold: The threshold of the sharing

        Returns:
            Dictionary of refreshed shares

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> ts = ThresholdSharing(group)
        >>> secret = group.random(ZR)
        >>> shares = ts.share(secret, 2, 3)
        >>> refreshed = ts.refresh_shares(shares, 2)
        >>> recovered = ts.reconstruct({1: refreshed[1], 3: refreshed[3]}, 2)
        >>> secret == recovered
        True
        """
        num_parties = len(shares)

        # Create shares of zero
        zero = self.group.init(ZR, 0)
        zero_shares = self.share(zero, threshold, num_parties)

        # Remap zero_shares to match party IDs in original shares
        party_ids = sorted(shares.keys())
        remapped_zero_shares = {}
        for idx, party_id in enumerate(party_ids):
            remapped_zero_shares[party_id] = zero_shares[idx + 1]

        return self.add_shares(shares, remapped_zero_shares)


class PedersenVSS(ThresholdSharing):
    """
    Pedersen VSS with information-theoretic hiding

    Uses two generators g, h for commitments where the discrete log
    relationship between g and h is unknown. This provides unconditional
    hiding of the secret, unlike Feldman VSS.

    >>> from charm.toolbox.eccurve import secp256k1
    >>> group = ECGroup(secp256k1)
    >>> pvss = PedersenVSS(group)
    >>> g = group.random(G)
    >>> h = group.random(G)
    >>> secret = group.random(ZR)
    >>> shares, blindings, comms = pvss.share_with_blinding(secret, g, h, 2, 3)
    >>> pvss.verify_pedersen_share(1, shares[1], blindings[1], comms, g, h)
    True
    >>> pvss.verify_pedersen_share(2, shares[2], blindings[2], comms, g, h)
    True
    >>> pvss.verify_pedersen_share(3, shares[3], blindings[3], comms, g, h)
    True
    >>> recovered = pvss.reconstruct({1: shares[1], 2: shares[2]}, 2)
    >>> secret == recovered
    True
    """

    def share_with_blinding(self, secret, g, h, threshold, num_parties):
        """
        Share with Pedersen commitments (information-theoretically hiding)

        Creates two polynomials:
        - f(x) with f(0) = secret for the actual shares
        - r(x) with r(0) = random blinding for hiding

        Commitments are C_j = g^{a_j} * h^{b_j} where a_j, b_j are
        coefficients of f and r respectively.

        Args:
            secret: The secret to share (ZR element)
            g: First generator point
            h: Second generator point (discrete log to g unknown)
            threshold: Minimum shares needed to reconstruct
            num_parties: Total number of parties

        Returns:
            Tuple of (shares_dict, blindings_dict, commitments_list)
            - shares_dict: {party_id: share_value}
            - blindings_dict: {party_id: blinding_value}
            - commitments_list: [C_0, C_1, ..., C_{t-1}]

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> pvss = PedersenVSS(group)
        >>> g, h = group.random(G), group.random(G)
        >>> secret = group.random(ZR)
        >>> shares, blindings, comms = pvss.share_with_blinding(secret, g, h, 2, 4)
        >>> all(pvss.verify_pedersen_share(i, shares[i], blindings[i], comms, g, h)
        ...     for i in range(1, 5))
        True
        """
        if threshold > num_parties:
            raise ValueError("threshold cannot exceed num_parties")
        if threshold < 1:
            raise ValueError("threshold must be at least 1")

        # Generate polynomial for secret: f(x) = a_0 + a_1*x + ... + a_{t-1}*x^{t-1}
        secret_coeffs = [secret]
        for _ in range(threshold - 1):
            secret_coeffs.append(self.group.random(ZR))

        # Generate polynomial for blinding: r(x) = b_0 + b_1*x + ... + b_{t-1}*x^{t-1}
        blinding_coeffs = []
        for _ in range(threshold):
            blinding_coeffs.append(self.group.random(ZR))

        # Compute Pedersen commitments: C_j = g^{a_j} * h^{b_j}
        commitments = []
        for j in range(threshold):
            C_j = (g ** secret_coeffs[j]) * (h ** blinding_coeffs[j])
            commitments.append(C_j)

        # Generate shares and blindings
        shares = {}
        blindings = {}
        for i in range(1, num_parties + 1):
            shares[i] = self._eval_polynomial(secret_coeffs, i)
            blindings[i] = self._eval_polynomial(blinding_coeffs, i)

        return shares, blindings, commitments

    def verify_pedersen_share(self, party_id, share, blinding, commitments, g, h):
        """
        Verify a share against Pedersen commitments

        Checks that g^{share} * h^{blinding} == prod_{j=0}^{t-1} C_j^{i^j}

        Args:
            party_id: The party's identifier (1 to n)
            share: The share value (ZR element)
            blinding: The blinding value (ZR element)
            commitments: List of Pedersen commitments [C_0, ..., C_{t-1}]
            g: First generator point
            h: Second generator point

        Returns:
            True if share is valid, False otherwise

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> pvss = PedersenVSS(group)
        >>> g, h = group.random(G), group.random(G)
        >>> secret = group.random(ZR)
        >>> shares, blindings, comms = pvss.share_with_blinding(secret, g, h, 3, 5)
        >>> pvss.verify_pedersen_share(3, shares[3], blindings[3], comms, g, h)
        True
        """
        # Compute g^{share} * h^{blinding}
        lhs = (g ** share) * (h ** blinding)

        # Compute prod_{j=0}^{t-1} C_j^{i^j}
        rhs = commitments[0]  # C_0^{i^0} = C_0
        i_power = self.group.init(ZR, party_id)

        for j in range(1, len(commitments)):
            rhs = rhs * (commitments[j] ** i_power)
            i_power = i_power * self.group.init(ZR, party_id)

        return lhs == rhs

    def combine_pedersen_commitments(self, commitments_list):
        """
        Combine multiple Pedersen commitments (for DKG)

        When multiple dealers contribute shares, their commitments
        can be combined element-wise.

        Args:
            commitments_list: List of commitment lists from different dealers

        Returns:
            Combined commitments list

        >>> from charm.toolbox.eccurve import secp256k1
        >>> group = ECGroup(secp256k1)
        >>> pvss = PedersenVSS(group)
        >>> g, h = group.random(G), group.random(G)
        >>> s1, s2 = group.random(ZR), group.random(ZR)
        >>> _, _, comms1 = pvss.share_with_blinding(s1, g, h, 2, 3)
        >>> _, _, comms2 = pvss.share_with_blinding(s2, g, h, 2, 3)
        >>> combined = pvss.combine_pedersen_commitments([comms1, comms2])
        >>> len(combined) == len(comms1)
        True
        """
        if not commitments_list:
            raise ValueError("Need at least one commitment list")

        num_coeffs = len(commitments_list[0])
        combined = list(commitments_list[0])

        for comms in commitments_list[1:]:
            if len(comms) != num_coeffs:
                raise ValueError("All commitment lists must have same length")
            for j in range(num_coeffs):
                combined[j] = combined[j] * comms[j]

        return combined


if __name__ == "__main__":
    import doctest
    doctest.testmod()
