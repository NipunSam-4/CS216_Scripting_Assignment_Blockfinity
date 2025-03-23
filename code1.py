from decimal import Decimal
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import logging
import time

# Set up logging
logging.basicConfig()
logging.getLogger("BitcoinRPC").setLevel(logging.DEBUG)

def connect_to_bitcoin_rpc():
    rpc_user = "nipun"
    rpc_password = "nipun"
    rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@127.0.0.1:18443", timeout=120)
    print("Connected to Bitcoin Core RPC")
    return rpc_connection

def main():
    p = connect_to_bitcoin_rpc()
    
    # Load or create wallet
    try:
        p.loadwallet("mywallet")
        print("\nWallet 'mywallet' loaded successfully\n")
    except JSONRPCException as e:
        if "Wallet file verification failed" in str(e) or "Wallet not found" in str(e):
            p.createwallet("mywallet")
            print("\nWallet 'mywallet' created successfully\n")
    
    # Generate legacy addresses
    addr_A = p.getnewaddress("", "legacy")
    addr_B = p.getnewaddress("", "legacy")
    addr_C = p.getnewaddress("", "legacy")
    
    print(f"Address A: {addr_A}")
    print(f"Address B: {addr_B}")
    print(f"Address C: {addr_C}\n")
    
    # Fund Address A
    txid_funding = p.sendtoaddress(addr_A, 1.0)
    print(f"Funding transaction: {txid_funding}\n")
    
    # Confirm transaction
    p.generatetoaddress(1, p.getnewaddress())

    # Get UTXO for Address A
    unspent = p.listunspent(1, 9999999, [addr_A])
    if not unspent:
        print("No UTXOs found for Address A")
        return
    
    utxo = unspent[0]
    print(f"UTXO for Address A: {utxo}\n")
    
    # Create transaction from A to B
    inputs = [{"txid": utxo["txid"], "vout": utxo["vout"]}]
    outputs = {addr_B: 0.5}
    
    change_amount = utxo["amount"] - Decimal('0.5') - Decimal('0.0001')
    if change_amount > 0:
        outputs[addr_A] = change_amount
    
    raw_tx_A_to_B = p.createrawtransaction(inputs, outputs)
    
    # Decode and print transaction
    decoded_tx_A_to_B = p.decoderawtransaction(raw_tx_A_to_B)
    print("Decoded transaction from A to B:")
    print(decoded_tx_A_to_B, "\n")
    
    # Extract and print ScriptPubKey from A to B
    vout_B = decoded_tx_A_to_B["vout"][0]  # Assuming B is the first output
    script_pubkey_B = vout_B["scriptPubKey"]["hex"]
    print(f"ScriptPubKey for Address B: {script_pubkey_B}\n")
    
    # Sign transaction
    signed_tx_A_to_B = p.signrawtransactionwithwallet(raw_tx_A_to_B)
    if signed_tx_A_to_B["complete"]:
        print("Transaction successfully signed\n")
    else:
        print("Transaction signing failed\n")
        return
    
    # Broadcast transaction
    txid_A_to_B = p.sendrawtransaction(signed_tx_A_to_B["hex"])
    print(f"Transaction A to B: {txid_A_to_B}\n")
    
    # Confirm transaction
    p.generatetoaddress(1, p.getnewaddress())
    
    # Get UTXO for Address B
    unspent = p.listunspent(1, 9999999, [addr_B])
    if not unspent:
        print("No UTXOs found for Address B\n")
        return
    
    utxo = unspent[0]
    print(f"UTXO for Address B: {utxo}\n")
    
    # Create transaction from B to C
    inputs = [{"txid": utxo["txid"], "vout": utxo["vout"]}]
    outputs = {addr_C: 0.25}
    
    change_amount = utxo["amount"] - Decimal('0.25') - Decimal('0.0001')
    if change_amount > 0:
        outputs[addr_B] = change_amount
    
    raw_tx_B_to_C = p.createrawtransaction(inputs, outputs)
    
    # Decode and print transaction
    decoded_tx_B_to_C = p.decoderawtransaction(raw_tx_B_to_C)
    print("Decoded transaction from B to C:")
    print(decoded_tx_B_to_C, "\n")
    
    # Sign transaction
    signed_tx_B_to_C = p.signrawtransactionwithwallet(raw_tx_B_to_C)
    if signed_tx_B_to_C["complete"]:
        print("Transaction successfully signed\n")
    else:
        print("Transaction signing failed\n")
        return
    
    # Decode signed transaction
    decoded_signed_tx_B_to_C = p.decoderawtransaction(signed_tx_B_to_C["hex"])
    print("Decoded signed transaction from B to C:")
    print(decoded_signed_tx_B_to_C, "\n")
    
    # Extract and print ScriptSig
    vin_B_to_C = decoded_signed_tx_B_to_C["vin"][0]  # First input from B
    script_sig_B_to_C = vin_B_to_C.get("scriptSig", {}).get("hex", "No ScriptSig found")
    print(f"ScriptSig for Address B to C: {script_sig_B_to_C}\n")
    
    # Broadcast transaction
    txid_B_to_C = p.sendrawtransaction(signed_tx_B_to_C["hex"])
    print(f"Transaction B to C: {txid_B_to_C}\n")
    
    # Confirm transaction
    p.generatetoaddress(1, p.getnewaddress())
    
    # Analyze the complete transaction
    complete_tx_B_to_C = p.getrawtransaction(txid_B_to_C, True)
    print("Complete transaction from B to C:")
    print(complete_tx_B_to_C, "\n")
    
    print("Analysis:")
    print(f"Transaction ID from A to B: {txid_A_to_B}")
    print(f"Transaction ID from B to C: {txid_B_to_C}")
    print(f"Raw Transaction Hex A to B: {raw_tx_A_to_B}")
    print(f"Raw Transaction Hex B to C: {raw_tx_B_to_C}")
    print(f"ScriptPubKey (locking script) from A to B: {script_pubkey_B}")
    print(f"ScriptSig (unlocking script) from B to C: {script_sig_B_to_C}")
    print("Use Bitcoin Debugger to validate these scripts.\n")

if __name__ == "__main__":
    main()