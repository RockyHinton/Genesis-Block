import hashlib
import json
import time

class Block:
    
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.compute_hash()
    
    def compute_hash(self): 
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()

    
class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        """
        Create the first block with index 0 and arbitrary previous hash.
        """
        genesis_block = Block(0, time.time(), "Genesis Block", "0")
        self.chain.append(genesis_block)

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, data):
        last_block = self.get_last_block()
        new_block = Block(
            index=last_block.index + 1,
            timestamp=time.time(),
            data=data,
            previous_hash=last_block.hash
        )
        self.chain.append(new_block)

    def is_chain_valid(self):
        """
        Verify each block's hash and the link between hashes.
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]

            # Recalculate the hash and compare
            if current.hash != current.compute_hash():
                return False

            if current.previous_hash != prev.hash:
                return False

        return True



# Test Blockchain
if __name__ == "__main__":
    blockchain = Blockchain()
    blockchain.add_block("First actual block")
    blockchain.add_block("Another block")

    for block in blockchain.chain:
        print(f"Index: {block.index}")
        print(f"Hash: {block.hash}")
        print(f"Previous Hash: {block.previous_hash}")
        print(f"Data: {block.data}")
        print("-" * 30)

    print("Is chain valid?", blockchain.is_chain_valid())
