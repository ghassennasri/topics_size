import base64
import requests
import json
import sys
from datetime import datetime, timedelta
from tqdm import tqdm
from prettytable import PrettyTable
import time
import os
import sys
import argparse


# Set the interval parameter with current time - 1 minute and current time
start_time = (datetime.utcnow() - timedelta(minutes=1)).isoformat() + "Z"
end_time = datetime.utcnow().isoformat() + "Z"
interval = f"{start_time}/{end_time}"

def clear_screen():
    if sys.platform.startswith("win"):
        os.system("cls")
    else:
        os.system("clear")


def get_topics(api_endpoint):
    headers = {
        "Authorization": f"Basic {BEARER_TOKEN_CLUSTER}",
    }
    response = requests.get(f"{api_endpoint}/kafka/v3/clusters/{CLUSTER_ID}/topics", headers=headers)
    return response.json()['data']

# New function to get the api_endpoint
def get_api_endpoint():
    headers = {
       "Authorization": f"Basic {BEARER_TOKEN_CLOUD}"
    }
    response = requests.get(f"https://api.confluent.cloud/cmk/v2/clusters/{CLUSTER_ID}?environment={ENV}", headers=headers)
    return response.json()['spec']['http_endpoint']




def get_retained_bytes(topic):
    headers = {
        "Accept": "application/json",
        "Authorization": f"Basic {BEARER_TOKEN_CLOUD}",
        "Content-Type": "application/json",
    }
    payload = {
        "aggregations": [{"metric": "io.confluent.kafka.server/retained_bytes"}],
        "filter": {
            "op": "AND",
            "filters": [
                {"field": "resource.kafka.id", "op": "EQ", "value": CLUSTER_ID},
                {"field": "metric.topic", "op": "EQ", "value": topic},
            ],
        },
        "granularity": "PT1M",
        "intervals": [interval],
    }
    response = requests.post("https://api.telemetry.confluent.cloud/v2/metrics/cloud/query", headers=headers, data=json.dumps(payload))
    return response.json()['data']


# Parse command-line arguments
parser = argparse.ArgumentParser(description="Get topic sizes from Confluent Cloud.")
parser.add_argument("--cluster-api-key", help="Cluster API key.", required=True)
parser.add_argument("--cluster-api-secret", help="Cluster API secret.", required=True)
parser.add_argument("--cloud-api-key", help="Cloud API key.", required=True)
parser.add_argument("--cloud-api-secret", help="Cloud API secret.", required=True)
parser.add_argument("--env", help="Cloud environment.", required=True)
parser.add_argument("--cluster-id", help="Cluster ID.", required=True)
parser.add_argument("--topics", nargs="+", help="List of specific topics to get the size of.", default=None)

args = parser.parse_args()

# Set API keys, secrets, and cluster ID from arguments
CLUSTER_API_KEY = args.cluster_api_key
CLUSTER_API_SECRET = args.cluster_api_secret
CLOUD_API_KEY = args.cloud_api_key
CLOUD_API_SECRET = args.cloud_api_secret
CLUSTER_ID = args.cluster_id
ENV=args.env
specified_topics = args.topics


BEARER_TOKEN_CLUSTER = base64.b64encode(f"{CLUSTER_API_KEY}:{CLUSTER_API_SECRET}".encode()).decode()
BEARER_TOKEN_CLOUD = base64.b64encode(f"{CLOUD_API_KEY}:{CLOUD_API_SECRET}".encode()).decode()



# Call the get_api_endpoint() function and pass the result to the get_topics() function
api_endpoint = get_api_endpoint()
topics = get_topics(api_endpoint)


if specified_topics:
    topics = [topic for topic in topics if topic['topic_name'] in specified_topics]
total_bytes = 0

# Initialize table with column headers
table = PrettyTable()
table.field_names = ["Topic", "Size (Bytes)"]

for topic in tqdm(topics, desc="Processing topics", unit="topic"):
    topic_name = topic['topic_name']
    retained_bytes = get_retained_bytes(topic_name)
    total_bytes += retained_bytes[0]['value'] if retained_bytes else 0
    table.add_row([topic_name, retained_bytes[0]['value'] if retained_bytes else 0])
    clear_screen()
    print(table)
    time.sleep(1)

print(f"Total number of requested topics: {len(topics)}")
print(f"Total retained bytes in MBytes: {total_bytes/ (1024 * 1024)}")
# print(table)

