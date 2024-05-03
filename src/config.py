# OSM NBI configs
NBI_URL="https://10.255.32.88:9999/osm"
USERNAME= PASSWORD = PROJECT = "admin"

# Thresholds
CPU_LOAD_THRESH = 80
MEM_LOAD_THRESH = 60

# Kafka broker configuration
KAFKA_SERVER = '10.255.32.88:10567'

# Kafka topic to consume from
KAFKA_TOPIC = 'k8s-cluster'

# Kafka consumer configuration
KAFKA_CONSUMER_CONF = {
    'bootstrap.servers': KAFKA_SERVER,
    'group.id': 'monitoring',
    'auto.offset.reset': 'latest'
}

KUBECTL_COMMAND = "/usr/local/bin/kubectl"
KUBECTL_CONFIG_PATH = "kube_config"