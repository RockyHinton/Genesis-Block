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

st.title("🔆 Solar Energy Trading Blockchain")
st.subheader("Simulating solar energy transactions, mining, and block creation")

# --- Show users ---
st.markdown("### 👥 Participants")
cols = st.columns(3)
for i, (name, keys) in enumerate(users.items()):
    with cols[i]:
        st.markdown(f"**{name}**")
        st.markdown("🔌 Public Key:")
        st.code(keys['public'][:60] + "...", language="text")

# --- Pending Transactions ---
st.markdown("### 🕒 Pending Energy Transactions")
if blockchain.pending_transactions:
    for tx in blockchain.pending_transactions:
        sender = tx.sender[:10] + "..." if tx.sender != "System" else "System"
        receiver = tx.receiver[:10] + "..." if tx.receiver != "System" else "System"
        energy = getattr(tx, "energy_amount", getattr(tx, "amount", "N/A"))
        fee = getattr(tx, "fee", "N/A")
        price = getattr(tx, "price_per_kwh", "N/A")
        st.markdown(
            f"🔁 **{sender}** ➡️ **{receiver}** | "
            f"Energy: `{energy} kWh` | Price: `{price}` | Fee: `{fee}`"
        )
else:
    st.info("No pending energy transactions.")

# --- Add New Transaction ---
st.markdown("### ➕ Create Energy Transaction")
col1, col2, col3 = st.columns(3)

with col1:
    sender_name = st.selectbox("Energy Seller", list(users.keys()))
with col2:
    receiver_name = st.selectbox("Energy Buyer", list(users.keys()))
with col3:
    energy_amount = st.number_input("Energy Amount (kWh)", min_value=1, step=1, value=10)

price_per_kwh = st.number_input("Price per kWh", min_value=1, value=10, step=1)
fee = st.slider("Transaction Fee (credits)", 0, 5, 1)

if st.button("Add Energy Transaction"):
    if sender_name == receiver_name:
        st.warning("Seller and buyer cannot be the same.")
    else:
        sender = users[sender_name]
        receiver = users[receiver_name]

        tx = Transaction(sender["public"], receiver["public"], energy_amount,
                         fee=fee, price_per_kwh=price_per_kwh)
        tx.sign_transaction(sender["private"])
        blockchain.add_transaction(tx)
        st.success("✅ Energy transaction added!")

# --- Mine Block ---
st.markdown("### ⛏️ Mine Pending Transactions")
miner = st.selectbox("Select Miner", list(users.keys()))
if st.button("Mine Block"):
    with st.spinner("⚙️ Mining energy transactions..."):
        time.sleep(1)
        blockchain.mine_pending_transactions(users[miner]["public"])
        st.success("✅ Block mined and added to the chain!")

# --- Visualize Blockchain ---
st.markdown("### 📦 Blockchain Overview")
for block in blockchain.chain:
    with st.expander(f"🔗 Block #{block.index}"):
        readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(block.timestamp))
        st.markdown(f"🕒 Timestamp: `{readable_time}`")
        st.markdown(f"⛓️ Previous Hash: `{block.previous_hash[:40]}...`")
        st.markdown(f"🔐 Current Hash: `{block.hash}`")
        st.markdown("#### ⚡ Energy Transactions & Rewards")
        if not block.transactions:
            st.write("No energy transactions in this block.")
        for tx in block.transactions:
            sender = tx.sender[:10] + "..." if tx.sender != "System" else "System"
            receiver = tx.receiver[:10] + "..." if tx.receiver != "System" else "System"
            fee = getattr(tx, "fee", "N/A")

            if tx.sender == "System":
                reward = getattr(tx, "reward_amount", tx.energy_amount)
                st.markdown(f"🏅 **Reward** ➡️ **{receiver}** | Tokens: `{reward}`")

            else:
                # Regular energy transaction
                energy = getattr(tx, "energy_amount", "N/A")
                price = getattr(tx, "price_per_kwh", "N/A")
                st.markdown(
                    f"🔁 **{sender}** ➡️ **{receiver}** | "
                    f"Energy: `{energy} kWh` | Price: `{price}` | Fee: `{fee}`"
                )

