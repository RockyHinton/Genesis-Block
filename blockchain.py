import hashlib
import json
import time
import ecdsa

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
        print(f"Block {self.index} mined with hash: {self.hash}")


    
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 4
        self.pending_transactions = []

    def create_genesis_block(self):
        return Block(0, time.time(), [], "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, sender, receiver, amount):
        transaction = Transaction(sender, receiver, amount)
        self.pending_transactions.append(transaction)


    def mine_pending_transactions(self, miner_address):
        valid_transactions = [tx for tx in self.pending_transactions if tx.is_valid()]
        new_block = Block(len(self.chain), time.time(), valid_transactions, self.get_latest_block().hash)
        new_block.mine_block(self.difficulty)

        # Reward miner
        reward_tx = Transaction("System", miner_address, 1)
        self.pending_transactions = [reward_tx]

        self.chain.append(new_block)


    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]

            # Recalculate the hash and compare
            if current.hash != current.compute_hash():
                return False

            # Check previous hash linkage
            if current.previous_hash != prev.hash:
                return False

        return True



class Transaction:

    def __init__(self, sender, receiver, amount, signature=None, public_key=None):
        self.sender = sender
        self. receiver = receiver
        self.amount = amount
        self.signature = signature
        self.public_key = public_key


    def __repr__(self):
        return f"Transaction({self.sender} -> {self.receiver}: {self.amount})"

    
    def to_dict(self, include_signature=False):
        data = {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount
        }
        if include_signature:
            data[signature] = self.signature
            data[public_key] = self.public_key
        return data
    
    
    def sign_transaction(self, private_key):
        if private_key.get_verifying_key().to_string().hex() != self.sender:
            raise Exception("You cannot sign transactions for other wallets!")

        tx_data = json.dumps(self.to_dict(), sort_keys=True).encode()
        signature_bytes = private_key.sign(tx_data)
        self.signature = signature_bytes.hex()


    
    def is_valid(self):
        if self.sender == "System":  # System transactions don't need a signature
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







# Create a new blockchain
my_chain = Blockchain()

# Add some transactions
my_chain.add_transaction("Alice", "Bob", 50)
my_chain.add_transaction("Bob", "Charlie", 30)

# Mine the transactions (mine a new block)
my_chain.mine_pending_transactions("Miner1")

# Add more transactions and mine another block
my_chain.add_transaction("Charlie", "Alice", 10)
my_chain.mine_pending_transactions("Miner2")

# Print the blockchain
for block in my_chain.chain:
    print(f"Block #{block.index}:")
    for tx in block.transactions:
        print(tx)
    print("Hash:", block.hash)
    print("-----")




# Generate keys
private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
public_key = private_key.get_verifying_key()

# Create and sign transaction
sender = public_key.to_string().hex()
tx = Transaction(sender, "receiver_placeholder", 100)
tx.sign_transaction(private_key)

# Print results
print("Signature (hex):", tx.signature)

# Verify
if tx.is_valid():
    print("✅ Signature is valid.")
else:
    print("❌ Signature is invalid.")





