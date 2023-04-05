'''
| From: "David Pointcheval, Olivier Sanders: Short Randomizable Signatures"
| Published in: Proceedings of the RSA Conference on Topics in Cryptology 2016
| Available from: https://dl.acm.org/doi/10.1007/978-3-319-29485-8_7
| Notes:
* type:           signature (blind signature)
* setting:        bilinear groups (asymmetric)
:Authors:    Ahmed Bakr
:Date:       04/2023
Description:
This file implements the four schemes:
    - Single Message Signature
        - Implemented in the class `PS_SigSingleMessage`
        - Tested in the function `single_message_main`
    - Multi Messages Signature
        - Implemented in the class `PS_SigMultiMessage`
        - Tested in the function `multi_message_main`
    - Blinded Single Message Signature
        - Implemented in the class `PS_BlindSingleMessageSig`
        - Tested in the function `blinded_single_message_main`
    - Blinded Multi Messages Signature
        - Implemented in the class `PS_SigMultiMessage`
        - Tested in the function `blinded_multi_message_main`
Notes:
    - The class `PS_Sig` defines four generic stubs functions that have to be implemented in every signature scheme, which are: keygen, sign, verify
    - The class `PS_BlindSig` inherits from `PS_Sig` and defines four generic stubs functions that have to be implemented in every signature scheme, which are: keygen, blind, proof_of_knowledge_of_commitment_secrets, sign, unblind, verify
    - The classes `PS_SigSingleMessage` and `PS_SigMultiMessage` inherit from `PS_Sig`
    - The classes `PS_BlindSingleMessageSig` and `PS_BlindMultiMessageSig` inherit from `PS_BlindSig`
 '''

import sys
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, pair
from charm.core.engine.util import objectToBytes
from charm.toolbox.PKSig import PKSig


def dump_to_zp_element(obj, group_obj):
    serialized_message = objectToBytes(obj, group_obj)
    return group_obj.hash(serialized_message)  # convert the serialized message to object from Z_p


class ShnorrInteractiveZKP():
    class Prover:
        def __init__(self, secret_t, secret_messages, groupObj):
            self.__r_t = None
            self.__r_ms = None
            self.group = groupObj
            self.__ms = [dump_to_zp_element(secret_message, groupObj) for secret_message in secret_messages]
            self.__t = secret_t # t is an element, so no need to transform it into an element

        def create_prover_commitments(self, pk):
            """
            1) This function is executed by the prover to send a random value to the verifier
            """
            if 'Ys' not in pk:
                pk['Ys'] = [pk['Y']] # Hack to convert it to an array because this method is general and used for both single and multiple messages
            self.__r_ms = [self.group.random() for _ in range(len(self.__ms))]
            self.__r_t = self.group.random()
            Y_pow_m_prod = pk['Ys'][0] ** self.__r_ms[0]
            for i in range(1, len(self.__ms)):
                Y_pow_m_prod *= pk['Ys'][i] ** self.__r_ms[i]
            Rc = (pk['g'] ** self.__r_t) * Y_pow_m_prod # Follow the same equation used to blind the message
            return Rc

        def create_proof(self, c):
            """
            3) This function is executed by the prover after he received the challenge value (c) from the verifier
            """
            s_t = self.__r_t + c * self.__t
            s_ms = [r_m + c * m for (r_m, m) in zip(self.__r_ms, self.__ms)]
            return (s_t, s_ms)  # proof

    class Verifier:

        def __init__(self, groupObj):
            self.group = groupObj

        def create_verifier_challenge(self):
            """
            2) This function is executed by the verifier after he had received the value u from the prover to send a challenge value to the prover.
            """
            self.c = self.group.random()
            return self.c

        def is_proof_verified(self, s_t, s_ms, pk, blinded_message, commitment):
            """
            4) This function is executed by the verifier to verify the authenticity of the proof sent by the prover
            """
            if 'Ys' not in pk:
                pk['Ys'] = [pk['Y']]  # Hack to convert it to an array because this method is general and used for both single and multiple messages
            Y_pow_m_prod = pk['Ys'][0] ** s_ms[0]
            for i in range(1, len(s_ms)):
                Y_pow_m_prod *= pk['Ys'][i] ** s_ms[i]
            if (pk['g'] ** s_t) * Y_pow_m_prod == (blinded_message ** self.c) * commitment:
                return True
            return False


class PS_Sig(PKSig):

    def __init__(self, groupObj):
        PKSig.__init__(self)
        self.group = groupObj

    def _dump_to_zp_element(self, obj):
        serialized_message = objectToBytes(obj, self.group)
        return self.group.hash(serialized_message) # convert the serialized message to object from Z_p

    def keygen(self):
        """
        This function is used to generate the secret key and the public key of the signer
        """
        print("This is a stub function. Implement it in the child class")

    def sign(self, sk, message):
        """
        This function is used for the signer to sign a message
        Inputs:
            - sk: Secret key of the signer
            - message: message to be signed
        Outputs:
            - sigma: Signature on the message
        """
        print("This is a stub function. Implement it in the child class")

    def verify(self, message, pk, sig) -> bool:
        """
        This function is used for the user to verify a signature on a specific message using the message and the public
        key of the signer.
        Inputs:
            - message: The message
            - pk: Public key
            - sig: signature
        Outputs:
            - True if the signature is valid on the message by the user whose public key is pk
            - False, otherwise
        """
        print("This is a stub function. Implement it in the child class")


class PS_BlindSig(PS_Sig):

    def __init__(self, groupObj):
        PS_Sig.__init__(self, groupObj)

    def keygen(self):
        """
        This function is used to generate the secret key and the public key of the signer
        """
        print("This is a stub function. Implement it in the child class")

    def blind(self, message):
        """
        This function takes a message and blinds it to return a blinded message.
        Inputs:
            - message: message to be blinded
        Outputs:
            - blinded_message: A blinded message
        """
        print("This is a stub function. Implement it in the child class")

    def sign(self, sk, blinded_message):
        """
        This function is used for the signer to sign a message
        Inputs:
            - sk: Secret key of the signer
            - blinded_message: A blinded message to be signed
        Outputs:
            - sigma_dash: Signature on the blinded message
        """
        print("This is a stub function. Implement it in the child class")

    def unblind(self, blinded_sig, t):
        """
        This function takes a blinded signature and returns the unblinded signature
        Inputs:
            - blinded_sig: Blinded signature
            - t: random number used to blind the original message
        Outputs:
            - sigma: unblinded signature
        """
        print("This is a stub function. Implement it in the child class")

    def proof_of_knowledge_of_commitment_secrets(self, t, messages, blinded_message, pk, group_obj, debug):
        """This function runs shnorr' interactive proof of knowledge"""
        shnorr_interactive_zkp = ShnorrInteractiveZKP()
        print("Prover wants to prove knowledge of the secret message to the signer (verifier) for him to agree to sign the message")
        prover = shnorr_interactive_zkp.Prover(secret_t=t, secret_messages=messages, groupObj=group_obj)
        verifier = shnorr_interactive_zkp.Verifier(groupObj=group_obj)
        commitments = prover.create_prover_commitments(pk)
        print("Prover sent commitments to the verifier")
        if debug:
            print("Rc = ", commitments)
        challenge = verifier.create_verifier_challenge()
        print("Verifier sends the challenge to the prover: ", challenge)
        s_t, s_m = prover.create_proof(challenge)
        print("Prover sends the proof of knowledge to the verifier: ")
        if debug:
            print("s_t: ", s_t)
            print("s_m: ", s_m)
        prover_knowledge_of_secret_message_status = verifier.is_proof_verified(s_t, s_m, pk, blinded_message, commitments)
        return prover_knowledge_of_secret_message_status


    def verify(self, message, pk, sig) -> bool:
        """
        This function is used for the user to verify a signature on a specific message using the message and the public
        key of the signer.
        Inputs:
            - message: The message
            - pk: Public key
            - sig: signature
        Outputs:
            - True if the signature is valid on the message by the user whose public key is pk
            - False, otherwise
        """
        print("This is a stub function. Implement it in the child class")


class PS_BlindSingleMessageSig(PS_BlindSig):

    def __init__(self, groupObj):
        PS_BlindSig.__init__(self, groupObj)

    def keygen(self):
        """
        This function is used to generate the secret key and the public key of the signer
        Outputs:
            - sk: Secret key
            - pk: public key
        """
        g = self.group.random(G1)
        g_tilde = self.group.random(G2)
        x = self.group.random()
        y = self.group.random()

        X = g ** x
        Y = g ** y
        X_tilde = g_tilde ** x
        Y_tilde = g_tilde ** y

        pk = {'g': g, 'Y': Y, 'g_tilde': g_tilde, 'X_tilde': X_tilde, 'Y_tilde': Y_tilde}
        sk = {'X': X}

        return sk, pk

    def blind(self, message, pk):
        """
        This function takes a message and blinds it to return a blinded message.
        Inputs:
            - message: message to be blinded
            - pk: pk is needed to know some of the public parameters used in message blinding
        Outputs:
            - C: A blinded message
            - t: Blind random value
        """
        m = self._dump_to_zp_element(message)  # serialize the message to an element
        t = self.group.random()
        C = (pk['g'] ** t) * (pk['Y'] ** m)

        return C, t

    def sign(self, sk, pk, blinded_message):
        """
        This function is used for the signer to sign a message
        Inputs:
            - sk: Secret key of the signer
            - pk: Public key of the signer
            - blinded_message: A blinded message to be signed
        Outputs:
            - sigma_dash: Signature on the blinded message
        """
        C = blinded_message
        u = self.group.random()
        sigma_dash_1 = pk['g'] ** u
        sigma_dash_2 = (sk['X'] * C) ** u
        sigma_dash = (sigma_dash_1, sigma_dash_2)

        return sigma_dash

    def unblind(self, blinded_sig, t):
        """
        This function takes a blinded signature and returns the unblinded signature
        Inputs:
            - blinded_sig: Blinded signature
            - t: random number used to blind the original message
        Outputs:
            - sigma: unblinded signature
        """
        sigma_dash_1, sigma_dash_2 = blinded_sig
        sigma_1 = sigma_dash_1
        sigma_2 = sigma_dash_2 / (sigma_dash_1 ** t)

        sigma = (sigma_1, sigma_2)
        return sigma

    def verify(self, message, pk, sig) -> bool:
        """
        This function is used for the user to verify a signature on a specific message using the message and the public
        key of the signer.
        Inputs:
            - message: The message
            - pk: Public key
            - sig: signature
        Outputs:
            - True if the signature is valid on the message by the user whose public key is pk
            - False, otherwise
        """
        sigma_1, sigma_2 = sig
        m = self._dump_to_zp_element(message)  # serialize the message to an element
        if pair(sigma_1, pk['X_tilde'] * (pk['Y_tilde'] ** m)) == pair(sigma_2, pk['g_tilde']):
            return True
        return False


class PS_BlindMultiMessageSig(PS_BlindSig):

    def __init__(self, groupObj):
        PS_BlindSig.__init__(self, groupObj)

    def keygen(self, num_messages):
        """
        This function is used to generate the secret key and the public key of the signer
        Outputs:
            - sk: Secret key
            - pk: public key
        """
        g = self.group.random(G1)
        g_tilde = self.group.random(G2)
        x = self.group.random()
        ys = [self.group.random() for i in range(num_messages)]

        X = g ** x
        Ys = [g ** y for y in ys]
        X_tilde = g_tilde ** x
        Ys_tilde = [g_tilde ** y for y in ys]

        pk = {'g': g, 'Ys': Ys, 'g_tilde': g_tilde, 'X_tilde': X_tilde, 'Ys_tilde': Ys_tilde}
        sk = {'X': X}

        return sk, pk

    def blind(self, messages, pk):
        """
        This function takes a message and blinds it to return a blinded message.
        Inputs:
            - messages: List of messages to be blinded
            - pk: pk is needed to know some of the public parameters used in message blinding
        Outputs:
            - C: A blinded message
            - t: Blind random value
        """
        ms = [self._dump_to_zp_element(message) for message in messages]  # serialize the message to an element
        t = self.group.random()
        Y_pow_m_product = pk['Ys'][0] ** ms[0]
        for i in range(1, len(ms)):
            Y_pow_m_product *= pk['Ys'][i] ** ms[i]
        C = (pk['g'] ** t) * Y_pow_m_product

        return C, t

    def sign(self, sk, pk, blinded_message):
        """
        This function is used for the signer to sign a message
        Inputs:
            - sk: Secret key of the signer
            - pk: Public key of the signer
            - blinded_message: A blinded message to be signed
        Outputs:
            - sigma_dash: Signature on the blinded message
        """
        C = blinded_message
        u = self.group.random()
        sigma_dash_1 = pk['g'] ** u
        sigma_dash_2 = (sk['X'] * C) ** u
        sigma_dash = (sigma_dash_1, sigma_dash_2)

        return sigma_dash

    def unblind(self, blinded_sig, t):
        """
        This function takes a blinded signature and returns the unblinded signature
        Inputs:
            - blinded_sig: Blinded signature
            - t: random number used to blind the original message
        Outputs:
            - sigma: unblinded signature
        """
        sigma_dash_1, sigma_dash_2 = blinded_sig
        sigma_1 = sigma_dash_1
        sigma_2 = sigma_dash_2 / (sigma_dash_1 ** t)

        sigma = (sigma_1, sigma_2)
        return sigma

    def verify(self, messages, pk, sig) -> bool:
        """
        This function is used for the user to verify a signature on a specific message using the message and the public
        key of the signer.
        Inputs:
            - messages: List of messages
            - pk: Public key
            - sig: signature
        Outputs:
            - True if the signature is valid on the message by the user whose public key is pk
            - False, otherwise
        """
        sigma_1, sigma_2 = sig
        ms = [self._dump_to_zp_element(message) for message in messages]  # serialize the message to an element
        Y_pow_m_product = pk['Ys_tilde'][0] ** ms[0]
        for i in range(1, len(ms)):
            Y_pow_m_product *= pk['Ys_tilde'][i] ** ms[i]
        if pair(sigma_1, pk['X_tilde'] * Y_pow_m_product) == pair(sigma_2, pk['g_tilde']):
            return True
        return False


class PS_SigSingleMessage(PS_Sig):

    def __init__(self, groupObj):
        PS_Sig.__init__(self, groupObj)

    def keygen(self):
        """
        This function is used to generate the secret key and the public key of the signer
        """
        g_tilde = self.group.random(G2)
        x = self.group.random()
        y = self.group.random()
        X_tilde = g_tilde ** x
        Y_tilde = g_tilde ** y

        pk = {'g_tilde': g_tilde, 'X_tilde': X_tilde, 'Y_tilde': Y_tilde}
        sk = {'x': x, 'y': y}

        return sk, pk

    def sign(self, sk, message):
        """
        This function is used for the signer to sign a message
        Inputs:
            - sk: Secret key of the signer
            - message: message to be signed
        Outputs:
            - sigma: Signature on the message
        """
        m = self._dump_to_zp_element(message) # serialize the message to an element
        h = self.group.random(G1)
        sigma = (h, h ** (sk['x'] + sk['y'] * m))

        return sigma

    def verify(self, message, pk, sig) -> bool:
        """
        This function is used for the user to verify a signature on a specific message using the message and the public
        key of the signer.
        Inputs:
            - message: The message
            - pk: Public key
            - sig: signature
        Outputs:
            - True if the signature is valid on the message by the user whose public key is pk
            - False, otherwise
        """
        sigma_1, sigma_2 = sig
        m = self._dump_to_zp_element(message)  # serialize the message to an element
        if pair(sigma_1, pk['X_tilde'] * (pk['Y_tilde'] ** m)) == pair(sigma_2, pk['g_tilde']):
            return True
        return False


class PS_SigMultiMessage(PS_Sig):

    def __init__(self, groupObj):
        PS_Sig.__init__(self, groupObj)

    def keygen(self, num_messages):
        """
        This function is used to generate the secret key and the public key of the signer
        Inputs:
            - num_message: Number of messages
        """
        g_tilde = self.group.random(G2)
        x = self.group.random()
        ys = [self.group.random() for i in range(num_messages)]
        X_tilde = g_tilde ** x
        Ys_tilde = [g_tilde ** y for y in ys]

        pk = {'g_tilde': g_tilde, 'X_tilde': X_tilde, 'Ys_tilde': Ys_tilde}
        sk = {'x': x, 'ys': ys}

        return sk, pk

    def sign(self, sk, messages):
        """
        This function is used for the signer to sign a message
        Inputs:
            - sk: Secret key of the signer
            - messages: List of messages to be signed
        Outputs:
            - sigma: Signature on the message
        """
        ms = [self._dump_to_zp_element(message) for message in messages]
        h = self.group.random(G1)
        Y_multiply_m_sum = sk['ys'][0] * ms[0]
        for i in range(1, len(ms)):
            Y_multiply_m_sum += sk['ys'][i] * ms[i]
        sigma = (h, h ** (sk['x'] + Y_multiply_m_sum))

        return sigma

    def verify(self, messages, pk, sig) -> bool:
        """
        This function is used for the user to verify a signature on a specific message using the message and the public
        key of the signer.
        Inputs:
            - messages: The list of messages
            - pk: Public key
            - sig: signature
        Outputs:
            - True if the signature is valid on the message by the user whose public key is pk
            - False, otherwise
        """
        sigma_1, sigma_2 = sig
        ms = [self._dump_to_zp_element(message) for message in messages]
        Y_tilde_pow_m_product = pk['Ys_tilde'][0] ** ms[0]
        for i in range(1, len(ms)):
            Y_tilde_pow_m_product *= pk['Ys_tilde'][i] ** ms[i]
        if pair(sigma_1, pk['X_tilde'] * Y_tilde_pow_m_product) == pair(sigma_2, pk['g_tilde']):
            return True
        return False


def single_message_main(debug=False):
    print("************************************** Single Message Main ************************************************")
    message = "Welcome to PS signature scheme"
    group_obj = PairingGroup('MNT224')
    ps_sig = PS_SigSingleMessage(group_obj)

    sk, pk = ps_sig.keygen()
    if debug:
        print("sk = ", sk)
        print("pk = ", pk)

    sigma = ps_sig.sign(sk, message)
    if debug:
        print("signature: ", sigma)
    verification_res = ps_sig.verify(message, pk, sigma)
    if verification_res:
        print("Verification is successful")
    else:
        print("Error! This signature is not valid on this message")
    print("***********************************************************************************************************")


def multi_message_main(debug=False):
    print("**************************************** Multi Messages Main **********************************************")
    messages = ["Welcome to PS signature scheme", "PS can be used in many applications", "Most importantly, it can generate anonymous signatures"]
    group_obj = PairingGroup('MNT224')
    ps_sig = PS_SigMultiMessage(group_obj)

    sk, pk = ps_sig.keygen(len(messages))
    if debug:
        print("sk = ", sk)
        print("pk = ", pk)

    sigma = ps_sig.sign(sk, messages)
    if debug:
        print("signature: ", sigma)
    verification_res = ps_sig.verify(messages, pk, sigma)
    if verification_res:
        print("Verification is successful")
    else:
        print("Error! This signature is not valid on this message")
    print("***********************************************************************************************************")


def blinded_single_message_main(debug=False):
    print("******************************** Blinded Single Message Main **********************************************")
    message = "Welcome to PS signature scheme"
    group_obj = PairingGroup('MNT224')
    ps_sig = PS_BlindSingleMessageSig(group_obj)

    sk, pk = ps_sig.keygen()
    if debug:
        print("sk = ", sk)
        print("pk = ", pk)

    blinded_message, t = ps_sig.blind(message, pk)
    if debug:
        print("Blinded Message: ", blinded_message)

    # Interactive ZKP
    # user proves knowledge of the secret message to the signer to accept to sign the blinded message
    prover_knowledge_of_secret_message_status = ps_sig.proof_of_knowledge_of_commitment_secrets(t, [message], blinded_message, pk, group_obj, debug)
    print("Verifier validation of the proof status: ", prover_knowledge_of_secret_message_status)

    if prover_knowledge_of_secret_message_status:
        blinded_signature = ps_sig.sign(sk, pk, blinded_message)
        if debug:
            print("Blinded signature: ", blinded_signature)

        signature = ps_sig.unblind(blinded_signature, t)
        if debug:
            print("Signature: ", signature)
        verification_res = ps_sig.verify(message, pk, signature)
        if verification_res:
            print("Verification is successful")
        else:
            print("Error! This signature is not valid on this message")
    else:
        print("Error! Proof of knowledge verification error")
    print("***********************************************************************************************************")


def blinded_multi_message_main(debug=False):
    print("******************************** Blinded Multi Message Main ***********************************************")
    messages = ["Welcome to PS signature scheme", "PS can be used in many applications", "Most importantly, it can generate anonymous signatures"]
    group_obj = PairingGroup('MNT224')
    ps_sig = PS_BlindMultiMessageSig(group_obj)

    sk, pk = ps_sig.keygen(len(messages))
    if debug:
        print("sk = ", sk)
        print("pk = ", pk)

    blinded_message, t = ps_sig.blind(messages, pk)
    if debug:
        print("Blinded Message: ", blinded_message)
    # Interactive ZKP
    # user proves knowledge of the secret message to the signer to accept to sign the blinded message
    prover_knowledge_of_secret_messages_status = ps_sig.proof_of_knowledge_of_commitment_secrets(t, messages,
                                                                                          blinded_message, pk,
                                                                                          group_obj, debug)
    print("Verifier validation of the proof status: ", prover_knowledge_of_secret_messages_status)

    if prover_knowledge_of_secret_messages_status:
        blinded_signature = ps_sig.sign(sk, pk, blinded_message)
        if debug:
            print("Blinded signature: ", blinded_signature)

        signature = ps_sig.unblind(blinded_signature, t)
        if debug:
            print("Signature: ", signature)

        verification_res = ps_sig.verify(messages, pk, signature)
        if verification_res:
            print("Verification is successful")
        else:
            print("Error! This signature is not valid on this message")
    else:
        print("Error! Proof of knowledge verification error")
    print("***********************************************************************************************************")


if __name__ == "__main__":
    debug = True
    single_message_main(debug)
    multi_message_main(debug)
    blinded_single_message_main(debug)
    blinded_multi_message_main(debug)
    print("done")