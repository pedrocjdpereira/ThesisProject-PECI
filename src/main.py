from flask import Flask, jsonify

from config import *
from nbi_k8s_connector import NBIConnector
from meao import MEAO

app = Flask(__name__)

@app.route('/containerInfo', methods=['GET'])
def get_container_info():
    return jsonify(ContainerInfo=meao.containerInfo)

if __name__ == '__main__':
    nbi_k8s_connector = NBIConnector(
        NBI_URL,
        KUBECTL_COMMAND,
        KUBECTL_CONFIG_PATH
    )

    meao = MEAO(
        nbi_k8s_connector,
        UPDATE_CONTAINER_IDS_FREQ
    )

    meao.start()

    app.run(host='0.0.0.0', port=8000)
