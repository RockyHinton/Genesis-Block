import hashlib
import json
import time
import ecdsa

from ecdsa import SigningKey, SECP256k1

# Constants
MINING_REWARD = 1

def generate_keys():
    private_key = SigningKey.generate(curve=SECP256k1)
    public_key = private_key.get_verifying_key()
    return public_key.to_string().hex(), private_key.to_string().hex()


class Block:
    def __init__(self, index, timestamp, transactions, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.compute_hash()

    def compute_hash(self): 
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()

    def mine_block(self, difficulty):
        target = '0' * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.compute_hash()
        print(f"✅ Block {self.index} mined with hash: {self.hash}")


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 4
        self.pending_transactions = []

    def create_genesis_block(self):
        return Block(0, time.time(), [], "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction):
        if transaction.is_valid():
            self.pending_transactions.append(transaction)
            print("✅ Transaction added")
        else:
            print("❌ Invalid transaction. Not added.")

    def mine_pending_transactions(self, miner_address):
        valid_transactions = [tx for tx in self.pending_transactions if tx.is_valid()]

        # Calculate fees
        total_fees = sum(tx.fee for tx in valid_transactions)

        # Add mining reward transaction to this block
        reward_amount = MINING_REWARD + total_fees
        reward_tx = Transaction("System", miner_address, reward_amount)
        valid_transactions.append(reward_tx)

        # Create new block
        new_block = Block(len(self.chain), time.time(), valid_transactions, self.get_latest_block().hash)
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

        # Clear pending transactions
        self.pending_transactions = []

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]

            if current.hash != current.compute_hash():
                return False
            if current.previous_hash != prev.hash:
                return False

        return True


class Transaction:
    def __init__(self, sender, receiver, amount, fee=0, signature=None, public_key=None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.fee = fee
        self.signature = signature
        self.public_key = public_key

    def __repr__(self):
        return f"Transaction({self.sender[:10]}... -> {self.receiver[:10]}...: {self.amount}, fee: {self.fee})"

    def to_dict(self, include_signature=False):
        data = {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "fee": self.fee
        }
        if include_signature:
            data["signature"] = self.signature
            data["public_key"] = self.public_key
        return data

    def sign_transaction(self, private_key):
        if private_key.get_verifying_key().to_string().hex() != self.sender:
            raise Exception("You cannot sign transactions for other wallets!")

        tx_data = json.dumps(self.to_dict(), sort_keys=True).encode()
        signature_bytes = private_key.sign(tx_data)
        self.signature = signature_bytes.hex()

    def is_valid(self):
        if self.sender == "System":
            return True
        if not self.signature:
            return False

        public_key_bytes = bytes.fromhex(self.sender)
        signature_bytes = bytes.fromhex(self.signature)

        verifying_key = ecdsa.VerifyingKey.from_string(public_key_bytes, curve=ecdsa.SECP256k1)

        try:
            tx_data = json.dumps(self.to_dict(), sort_keys=True).encode()
            return verifying_key.verify(signature_bytes, tx_data)
        except ecdsa.BadSignatureError:
            return False


# ----- Example usage for testing -----

if __name__ == "__main__":
    # Generate ECDSA key pair for sender
    private_key = SigningKey.generate(curve=SECP256k1)
    public_key = private_key.get_verifying_key()
    sender_address = public_key.to_string().hex()

    # Example receiver
    receiver_private = SigningKey.generate(curve=SECP256k1)
    receiver_public = receiver_private.get_verifying_key()
    receiver_address = receiver_public.to_string().hex()

    # Valid transaction
    valid_tx = Transaction(sender_address, receiver_address, 100, fee=2)
    valid_tx.sign_transaction(private_key)

    # Invalid transaction
    invalid_tx = Transaction(sender_address, receiver_address, 100, fee=5)
    invalid_tx.signature = "deadbeef" * 16  # clearly invalid

    # Setup blockchain
    chain = Blockchain()

    # Add transactions
    print("\nAdding VALID transaction...")
    chain.add_transaction(valid_tx)

    print(f"\nAdding INVALID transaction (fee={invalid_tx.fee})...")
    chain.add_transaction(invalid_tx)

    # Mine block
    print("\n⛏️  Mining block...")
    chain.mine_pending_transactions("miner_address_123")

    # Print chain
    print("\n🧱 Blockchain contents:")
    for block in chain.chain:
        readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(block.timestamp))
        print(f"\nBlock #{block.index} @ {readable_time} ({block.timestamp})")
        for tx in block.transactions:
            print(f"  - {tx}")
        print(f"Hash: {block.hash}")
        print("-----")




