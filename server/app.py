from itertools import count
from flask import Flask, jsonify, redirect, request
from flask_cors import CORS

from web3 import Web3
import web3
import web3.auto.gethdev as GethDev
import os
from util import tx_formatter
from web3._utils.method_formatters import to_hex_if_integer
import json
app = Flask(__name__)
CORS(app, resources={r"/": {"origins": "http://localhost:3000"}})

anvil_rpc_url = os.environ['ANVIL_RPC_URL']
block_number = os.environ["BLOCK_NUMBER"]
debug_rpc_url = os.environ['DEBUG_RPC_URL']
frontend_url = os.environ['FRONTEND_URL']

local_w3 = Web3(Web3.HTTPProvider(anvil_rpc_url))
local_w3.middleware_onion.inject(
    web3.middleware.geth_poa_middleware,
    layer=0
)

debug_w3 = Web3(Web3.HTTPProvider(debug_rpc_url))
debug_w3.middleware_onion.inject(
    web3.middleware.geth_poa_middleware,
    layer=0
)
gas_price = int(debug_w3.eth.get_block(block_number)["baseFeePerGas"])

counter = 0


tx_data = {}
trace_result = {}


@app.route("/")
def index():
    return redirect(frontend_url)


@app.route("/connected")
def connected():
    response = jsonify({"result": "false"})
    if local_w3.isConnected():
        response = jsonify({"result": "true"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route("/gasPrice", methods=["POST", "GET"])
def getGasPrice():
    response = jsonify({"gasPrice": gas_price})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route("/getTx/<txid>", methods=["GET"])
def getTransaction():
    txId = int(txid)
    traces = trace_result[txId]
    result = []
    for trace in traces:
        result.append(
            {"from": trace["from"], "to": trace["to"], "indentation": 0})
    response = jsonify({"traces": result, "transactionData": tx_data[txId]})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/sendTxn", methods=['POST'])
def sendTransaction():
    
    calldata = tx_formatter({
        "to": local_w3.toChecksumAddress(request.form["to"]),
        "from": local_w3.toChecksumAddress(request.form["from"]),
        "value": int(request.form["value"]),
        "data": request.form["data"],
        "gasPrice": int(request.form["gasPrice"])
    })
    hexbytes = local_w3.manager.request_blocking(
        "eth_sendUnsignedTransaction", [calldata])

    traceResults = sendDump(calldata, int(os.getenv("BLOCK_NUMBER")))
    traceResults = json.loads(traceResults)
    trace_result[counter] = traceResults
    tx_data[counter] = calldata
    
    response = jsonify({
        "return": hexbytes,
        "traceResults": Web3.toJSON(traceResults),
        "txIndex": counter
    })
    counter += 1 
    response.headers.add('Access-Control-Allow-Origin', '*')
    
    return response


def sendDump(txData, block):
    dump = json.loads(local_w3.manager.request_blocking(
        "anvil_dumpStateJson", []))["accounts"]
    for addr, state in dump.items():
        state["nonce"] = to_hex_if_integer(state["nonce"])
        dump[addr] = state
    # tracer = ""
    # with open('/Users/haowang/coding/fip/server/tracer.txt') as f:
    #     tracer = f.readlines()
    trace_result = debug_w3.manager.request_blocking(
        "debug_traceCall",
        [txData, to_hex_if_integer(block), {
            "stateOverrides": dump,
            "tracer": "callTracer"
        }])
    return trace_result


@app.route("/getTrace", methods=['POST'])
def getTrace():
    return trace_result
