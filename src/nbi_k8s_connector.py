import json
import subprocess
import yaml
from osmclient import client
from osmclient.common.exceptions import ClientException

class NBIConnector:

    def __init__(self, osm_hostname, kubectl_command, kubectl_config_path) -> None:
        self.osm_hostname = osm_hostname
        self.kubectl_command = kubectl_command
        self.kubectl_config_path = kubectl_config_path
        self.nbi_client = client.Client(host=self.osm_hostname, port=9999,sol005=True)
        try:
            kubectl_config = self.nbi_client.k8scluster.list()[0]
        except Exception as e:
            print("ERROR: Could not get kube config")
            exit(1)
        with open(self.kubectl_config_path, 'w') as file:
            yaml.dump(kubectl_config["credentials"], file)

    def getNodeSpecs(self):
        nodeSpecs = {}

        command = (
            "{} --kubeconfig={} get nodes -o=json".format(
                self.kubectl_command,
                self.kubectl_config_path,
            )
        )
        try:
            # Execute the kubectl command and capture the output
            node_info = json.loads(subprocess.check_output(command.split()))
        except subprocess.CalledProcessError as e:
            # Handle any errors if the command fails
            print("Error executing kubectl command:", e)
            return None

        for node in node_info["items"]:
            nodeSpecs[node["metadata"]["labels"]["kubernetes.io/hostname"]] = {
                "num_cpu_cores": int(node["status"]["allocatable"]["cpu"]),
                "memory_size": int(node["status"]["allocatable"]["memory"][:-2])/pow(1024,2),
            }
        
        return nodeSpecs
    
    def getContainerInfo(self):
        ns_instances = self.nbi_client.ns.list()
        
        if len(ns_instances) < 1:
            print('ERROR: No deployed ns instances')
        elif 'code' in ns_instances[0].keys():
            print('ERROR: Error calling ns_instances endpoint')

        containerInfo = []

        for ns_instance in ns_instances:
            ns_id = ns_instance["_id"]
            vnf_ids = ns_instance["constituent-vnfr-ref"]
            vnf_instances = {}
            for vnf_id in vnf_ids:
                vnfContent = self.nbi_client.vnf.get(vnf_id)
                vnf_instances[vnfContent["member-vnf-index-ref"]] = vnfContent["_id"]
            if "deployed" not in ns_instance["_admin"].keys():
                break
            kdu_instances = ns_instance["_admin"]["deployed"]["K8s"]
            for kdu in kdu_instances:
                kdu_instance = kdu["kdu-instance"]
                member_vnf_index = kdu["member-vnf-index"]
                namespace = kdu["namespace"]
                vnf_id = vnf_instances[member_vnf_index]

                command = (
                    "{} --kubeconfig={} --namespace={} get pods -l ns_id={} -o=json".format(
                        self.kubectl_command,
                        self.kubectl_config_path,
                        namespace,
                        ns_id,
                    )
                )
                try:
                    # Execute the kubectl command and capture the output
                    k8s_info = json.loads(subprocess.check_output(command.split()))
                except subprocess.CalledProcessError as e:
                    # Handle any errors if the command fails
                    print("Error executing kubectl command:", e)
                    return None

                for pod in k8s_info["items"]:
                    nodeName = pod["spec"]["nodeName"]
                    containers = pod["status"]["containerStatuses"]
                    for container in containers:
                        if "containerID" in container:
                            id = container["containerID"]
                            containerInfo.append({
                                "id": id.strip('"').split('/')[-1],
                                "ns_id": ns_id,
                                "vnf_id": vnf_id,
                                "kdu_id": kdu_instance,
                                "node": nodeName,
                                }
                            )

        return containerInfo