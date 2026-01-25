#!/usr/bin/env python3
"""
XRPL Threshold ECDSA Demo with Memos

This script demonstrates end-to-end XRPL integration using the DKLS23
threshold ECDSA implementation in Charm:

1. Creates two threshold wallets (A and B) using 2-of-3 threshold ECDSA
2. Funds wallet A from the XRPL testnet faucet
3. Sends 10 XRP from wallet A to wallet B with a memo
4. Verifies the transaction and memo on the ledger

Requirements:
    pip install xrpl-py

Usage:
    python examples/xrpl_memo_demo.py
"""

import sys
import time

# Charm imports
from charm.toolbox.eccurve import secp256k1
from charm.toolbox.ecgroup import ECGroup
from charm.schemes.threshold.dkls23_sign import DKLS23
from charm.schemes.threshold.xrpl_wallet import (
    XRPLThresholdWallet,
    XRPLClient,
    sign_xrpl_transaction,
    create_payment_with_memo,
    get_transaction_memos,
    encode_memo_data,
    get_secp256k1_generator
)


def create_threshold_wallet(name: str, threshold: int = 2, num_parties: int = 3):
    """Create a threshold wallet and return all components."""
    print(f"\n{'='*60}")
    print(f"Creating {name}: {threshold}-of-{num_parties} Threshold Wallet")
    print('='*60)
    
    group = ECGroup(secp256k1)
    dkls = DKLS23(group, threshold=threshold, num_parties=num_parties)
    # Use the standard secp256k1 generator (NOT a random point!)
    # This is required for signatures to be verifiable by external systems like XRPL
    g = get_secp256k1_generator(group)
    
    print("  Generating distributed keys...")
    key_shares, public_key = dkls.distributed_keygen(g)
    
    wallet = XRPLThresholdWallet(group, public_key)
    
    print(f"  Classic Address: {wallet.get_classic_address()}")
    print(f"  Public Key: {wallet.get_public_key_hex()[:40]}...")
    
    return {
        'wallet': wallet,
        'dkls': dkls,
        'key_shares': key_shares,
        'generator': g,
        'group': group
    }


def main():
    print("\n" + "="*60)
    print("  XRPL Threshold ECDSA Demo with Memos")
    print("  Using DKLS23 Protocol from Charm")
    print("="*60)
    
    # Step 1: Create two threshold wallets
    print("\n[Step 1] Creating two threshold wallets...")
    wallet_a = create_threshold_wallet("Wallet A (Sender)")
    wallet_b = create_threshold_wallet("Wallet B (Receiver)")
    
    address_a = wallet_a['wallet'].get_classic_address()
    address_b = wallet_b['wallet'].get_classic_address()
    
    print(f"\n  Wallet A: {address_a}")
    print(f"  Wallet B: {address_b}")
    
    # Step 2: Connect to XRPL testnet
    print("\n[Step 2] Connecting to XRPL Testnet...")
    client = XRPLClient(is_testnet=True)
    print(f"  Connected to: {client.url}")
    
    # Step 3: Fund Wallet A from faucet
    print("\n[Step 3] Funding Wallet A from testnet faucet...")
    print("  (This may take up to 60 seconds...)")
    
    try:
        faucet_result = XRPLClient.fund_from_faucet(address_a, timeout=60)
        print(f"  Faucet funding successful!")
        
        # Wait for ledger to update
        print("  Waiting for ledger to update...")
        time.sleep(5)
        
        # Verify account
        if client.does_account_exist(address_a):
            balance = client.get_balance(address_a)
            sequence = client.get_account_sequence(address_a)
            print(f"  Balance: {balance / 1_000_000:.2f} XRP")
            print(f"  Sequence: {sequence}")
        else:
            print("  ERROR: Account not found after funding!")
            sys.exit(1)
            
    except Exception as e:
        print(f"  Faucet error: {e}")
        print("  Please try again later or fund manually.")
        sys.exit(1)
    
    # Step 4: Create payment transaction with memo
    print("\n[Step 4] Creating payment transaction with memo...")
    
    memo_message = "test charmed xrpl demo"
    amount_drops = "10000000"  # 10 XRP
    
    print(f"  Amount: 10 XRP ({amount_drops} drops)")
    print(f"  Memo: \"{memo_message}\"")
    print(f"  Memo (hex): {encode_memo_data(memo_message)}")
    
    tx = create_payment_with_memo(
        account=address_a,
        destination=address_b,
        amount=amount_drops,
        memo_text=memo_message,
        sequence=sequence,
        fee="12"
    )
    
    print(f"  Transaction created: Payment from A to B")
    
    # Step 5: Generate presignatures and sign
    print("\n[Step 5] Signing transaction with threshold parties [1, 2]...")
    
    presigs = wallet_a['dkls'].presign(
        [1, 2], 
        wallet_a['key_shares'], 
        wallet_a['generator']
    )
    print("  Presignatures generated")
    
    signed_blob = sign_xrpl_transaction(
        wallet_a['dkls'],
        wallet_a['wallet'],
        [1, 2],
        presigs,
        wallet_a['key_shares'],
        tx,
        wallet_a['generator']
    )
    print(f"  Signed blob: {signed_blob[:60]}...")
    
    # Step 6: Submit transaction
    print("\n[Step 6] Submitting transaction to XRPL testnet...")

    try:
        result = client.submit_transaction(signed_blob)
        engine_result = result.get('engine_result', 'UNKNOWN')
        tx_hash = result.get('tx_json', {}).get('hash', 'UNKNOWN')

        print(f"  Engine Result: {engine_result}")
        print(f"  Transaction Hash: {tx_hash}")

        if engine_result != 'tesSUCCESS':
            print(f"  WARNING: Transaction may not have succeeded!")
            print(f"  Full result: {result}")
    except Exception as e:
        print(f"  Submission error: {e}")
        sys.exit(1)

    # Step 7: Wait for validation and verify
    print("\n[Step 7] Waiting for transaction validation...")
    time.sleep(5)  # Wait for validation

    try:
        # Look up the transaction
        tx_details = client.get_transaction(tx_hash)
        validated = tx_details.get('validated', False)

        print(f"  Validated: {validated}")

        # Check memos in the transaction
        memos = get_transaction_memos(tx_details)
        if memos:
            print(f"  Memos found: {len(memos)}")
            for i, memo in enumerate(memos):
                print(f"    Memo {i+1}:")
                if 'data' in memo:
                    print(f"      Data: \"{memo['data']}\"")
                if 'type' in memo:
                    print(f"      Type: {memo['type']}")
        else:
            print("  No memos found in transaction")

    except Exception as e:
        print(f"  Transaction lookup error: {e}")

    # Step 8: Verify Wallet B received funds
    print("\n[Step 8] Verifying Wallet B received funds...")

    try:
        if client.does_account_exist(address_b):
            balance_b = client.get_balance(address_b)
            print(f"  Wallet B Balance: {balance_b / 1_000_000:.2f} XRP")
            print(f"  SUCCESS: Wallet B received funds!")
        else:
            print("  Wallet B not yet activated (needs more XRP)")
            print("  Note: XRPL requires 10 XRP minimum to activate account")
    except Exception as e:
        print(f"  Balance check error: {e}")

    # Summary
    print("\n" + "="*60)
    print("  Demo Complete!")
    print("="*60)
    print(f"\n  Wallet A: {address_a}")
    print(f"  Wallet B: {address_b}")
    print(f"  Transaction: {tx_hash}")
    print(f"  Memo: \"{memo_message}\"")
    print(f"\n  View on explorer:")
    print(f"  https://testnet.xrpl.org/transactions/{tx_hash}")
    print()


if __name__ == '__main__':
    main()

