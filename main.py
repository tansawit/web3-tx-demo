import json
from web3 import Web3

# Infura endpoint to query the Eth blockchain
ETH_MAINNET_RPC_URL = "https://mainnet.infura.io/v3/14461acd6f534d96bfc383dfd7bc4bde"
UNISWAP_ROUTER_ADDRESS = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
UNISWAP_ROUTER_ABI_JSON = "abi/UniswapV2Router02.json"
UNISWAP_ROUTER_ABI = json.load(open(UNISWAP_ROUTER_ABI_JSON))

# Example transaction hashes
ADD_LIQUIDITY_TX = "0xb41699341b4d0e38ca8838fe53112c56b5588aff05cc14cd5ab7b7ec27d01ca3"
REMOVE_LIQUIDITY_TX = "0x4cd8f17441f10b19ae65e17555da350720f7d8a8ecb6d4e2ce5a6f865ac7f1ca"
SWAP_TX = "0xdf500e039b3560899e6eda2d18cdcc8844dc1111c61470d23201588f4563804b"

# Create web3 instance using Infura endpoint
web3 = Web3(Web3.HTTPProvider(ETH_MAINNET_RPC_URL))


def get_function_signature(function_name):
    # get function parameters and information from ABI
    function_obj = [obj for obj in UNISWAP_ROUTER_ABI if obj["type"] == "function" and obj["name"] == function_name][0]
    # construct full function signature from ABI
    parameters = [(input["type"], input["name"]) for input in function_obj["inputs"]]
    function_signature = f"{function_name}({','.join([' '.join(pair) for pair in parameters])})"
    return function_signature


def get_function_called(hash):
    tx = web3.eth.get_transaction(hash)
    # get the first 8 bytes of the input hex to check which function is called
    # https://stackoverflow.com/questions/55258332/find-the-function-name-and-parameter-from-input-data
    tx_function_sig_hash = tx.input[0:8]
    for obj in UNISWAP_ROUTER_ABI:
        if obj["type"] == "function":
            # construct function signature from function name and parameter types
            # and hash using keccak256 + take first 8 bytes
            parameters = ",".join([param["type"] for param in obj["inputs"]])
            current_function_sig_hash = Web3.keccak(text=f"{obj['name']}({parameters})").hex()
            # compare current function hash with tx_function_sig hash
            if tx_function_sig_hash == current_function_sig_hash[0:8]:
                function_called = obj["name"]
                called_function_signature = get_function_signature(function_called)
                return function_called, called_function_signature


def decode_tx_details(hash):
    # Create Uniswapswap contract object
    uniswap_router_contract = web3.eth.contract(address=UNISWAP_ROUTER_ADDRESS, abi=UNISWAP_ROUTER_ABI)
    # Use Infura endpoint to fetch tx data
    tx = web3.eth.get_transaction(hash)
    # use the contract's ABI (https://docs.soliditylang.org/en/v0.8.4/abi-spec.html) to decode
    # the parameters of the function call in the tx
    decoded_tx_input = uniswap_router_contract.decode_function_input(tx.input)
    return decoded_tx_input


def main():
    txs = [ADD_LIQUIDITY_TX, REMOVE_LIQUIDITY_TX, SWAP_TX]
    for tx in txs:
        (function_called, called_function_signature) = get_function_called(tx)
        tx_details = decode_tx_details(tx)
        print(f"function called: {function_called}")
        print(f"function signature: {called_function_signature}")
        print(f"tx details:\n {tx_details}")
        print("\n")


if __name__ == "__main__":
    main()
