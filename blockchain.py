import hashlib
import json
import time

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
        # Create a block from the pending transactions
        new_block = Block(len(self.chain), time.time(), self.pending_transactions, self.get_latest_block().hash)
        new_block.mine_block(self.difficulty)

        # Reward the miner for mining the block
        self.add_transaction("System", miner_address, 1)

        # Add the block to the chain
        self.chain.append(new_block)

        # Reset the list of pending transactions
        self.pending_transactions = []

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

    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self. receiver = receiver
        self.amount = amount

    def __repr__(self):
        return f"Transaction({self.sender} -> {self.receiver}: {self.amount})"

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount
        }





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


