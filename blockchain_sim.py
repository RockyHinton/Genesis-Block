import streamlit as st
from blockchain import Blockchain, Transaction
from ecdsa import SigningKey, SECP256k1
import time

# --- Initialization ---
@st.cache_resource
def init_blockchain():
    return Blockchain()

blockchain = init_blockchain()

# Generate 3 example users with public/private key pairs
@st.cache_resource
def init_users():
    users = {}
    for i in range(3):
        sk = SigningKey.generate(curve=SECP256k1)
        pk = sk.get_verifying_key()
        users[f"User {i+1}"] = {"public": pk.to_string().hex(), "private": sk}
    return users

users = init_users()

st.title("💸 Blockchain Transaction Simulator")
st.subheader("Simulating transactions, mining and block creation")

# --- Show users ---
st.markdown("### 👥 Users")
cols = st.columns(3)
for i, (name, keys) in enumerate(users.items()):
    with cols[i]:
        st.markdown(f"**{name}**")
        st.code(keys['public'][:60] + "...", language="text")

# --- Pending Transactions ---
st.markdown("### 🕒 Pending Transactions")
if blockchain.pending_transactions:
    for tx in blockchain.pending_transactions:
        st.markdown(f"🔁 **{tx.sender[:10]}...** ➡️ **{tx.receiver[:10]}...** | Amount: `{tx.amount}` | Fee: `{tx.fee}`")
else:
    st.info("No transactions yet.")

# --- Add New Transaction ---
st.markdown("### ➕ Create a Transaction")
col1, col2, col3 = st.columns(3)

with col1:
    sender_name = st.selectbox("Sender", list(users.keys()))
with col2:
    receiver_name = st.selectbox("Receiver", list(users.keys()))
with col3:
    amount = st.number_input("Amount", min_value=1, step=1, value=10)

fee = st.slider("Transaction Fee", 0, 5, 1)

if st.button("Add Transaction"):
    if sender_name == receiver_name:
        st.warning("Sender and receiver cannot be the same.")
    else:
        sender = users[sender_name]
        receiver = users[receiver_name]

        tx = Transaction(sender["public"], receiver["public"], amount, fee=fee)
        tx.sign_transaction(sender["private"])
        blockchain.add_transaction(tx)

# --- Mine Block ---
st.markdown("### ⛏️ Mine Pending Transactions")
miner = st.selectbox("Choose Miner", list(users.keys()))
if st.button("Mine Block"):
    with st.spinner("⛏️ Mining in progress..."):
        time.sleep(1)  # artificial delay for effect
        blockchain.mine_pending_transactions(users[miner]["public"])
        st.success("Block mined and added to the chain!")

# --- Visualize Blockchain ---
st.markdown("### 🧱 Blockchain")
for block in blockchain.chain:
    with st.expander(f"📦 Block #{block.index}"):
        readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(block.timestamp))
        st.markdown(f"⏱️ Timestamp: `{readable_time}`")
        st.markdown(f"🔗 Previous Hash: `{block.previous_hash[:40]}...`")
        st.markdown(f"🔐 Hash: `{block.hash}`")
        st.markdown("**📄 Transactions:**")
        if not block.transactions:
            st.write("No transactions in this block.")
        for tx in block.transactions:
            sender = tx.sender[:10] + "..." if tx.sender != "System" else "System"
            st.markdown(f"- {sender} ➡️ {tx.receiver[:10]}... | Amount: `{tx.amount}` | Fee: `{tx.fee}`")

