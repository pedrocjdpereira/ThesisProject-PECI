import os
from flask import Flask, jsonify, redirect
from nbi_k8s_connector import NBIConnector
from meao import MEAO

app = Flask(__name__)

@app.route('/containerInfo', methods=['GET'])
def get_container_info():
    return jsonify(ContainerInfo=meao.get_container_ids())

@app.route('/nodeSpecs', methods=['GET'])
def get_node_specs():
    return jsonify(NodeSpecs=meao.get_node_specs())

from flask import request

@app.route('/nodeSpecs/<hostname>', methods=['GET'])
def get_node_specs_hostname(hostname):
    return jsonify(NodeSpecs=meao.get_node_specs(hostname))

@app.route('/nodeSpecs/update', methods=['GET'])
def update_node_specs():
    meao.update_node_specs()
    return redirect('/nodeSpecs')

if __name__ == '__main__':
    nbi_k8s_connector = NBIConnector(
        os.environ.get("OSM_HOSTNAME"),
        os.environ.get("KUBECTL_COMMAND"),
        os.environ.get("KUBECTL_CONFIG_PATH")
    )

    meao = MEAO(
        nbi_k8s_connector,
        int(os.environ.get("UPDATE_CONTAINER_IDS_FREQ")),
    )

    meao.start()

    app.run(host='0.0.0.0', port=8000)
