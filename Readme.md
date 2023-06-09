# Confluent cloud Kafka Topic Size Tool

This Python script retrieves the size of Kafka topics from a Confluent Cloud cluster. It fetches the latest retained bytes for each topic and displays them in a human-readable table. If no topics are specified, the script will print the size for all topics in the cluster.
The script uses Confluent cloud metrics api. It fetches the current value of the metric **retained_bytes**.
The query payload is;
```json
{
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
```
**interval** is **[current_time-1min,current_time]**

Please refer to https://api.telemetry.confluent.cloud/docs/descriptors/datasets/cloud and https://docs.confluent.io/cloud/current/monitoring/metrics-api.html 

## Requirements

- Python 3.x
- `requests` library
- `prettytable` library
- `tqdm` library

You can install the required libraries using the following command:

```bash
pip install requests prettytable tqdm
```
## Usage

Save the script as `topic_size.py`. To run the script, use the following command with the required command-line arguments:

```bash
python topic_size.py --cluster-api-key <cluster-api-key> \
                     --cluster-api-secret <cluster-api-secret> \
                     --cloud-api-key <cloud-api-key> \
                     --cloud-api-secret <cloud-api-secret> \
                     --env <environment> \
                     --cluster-id <cluster-id> \
                     [--topics <topic1> <topic2> ...]
```
### Command-line Arguments

- `--cluster-api-key`: The Cluster API key. (required)
- `--cluster-api-secret`: The Cluster API secret. (required)
- `--cloud-api-key`: The Cloud API key. (required)
- `--cloud-api-secret`: The Cloud API secret. (required)
- `--env`: The Confluent Cloud environment. (required)
- `--cluster-id`: The Cluster ID. (required)
- `--topics`: A list of specific topics to get the size of. If this argument is not provided, the script will print the size for all topics in the cluster. (optional)

Refer to https://docs.confluent.io/cloud/current/access-management/authenticate/api-keys/api-keys.html to create cloud/cluster api keys

Example command:

```bash
python topic_size.py --cluster-api-key FYQOARIQRY4MHC3H \
                     --cluster-api-secret xxxxxxxxxxxxxxxxxxxxxxx \
                     --cloud-api-key LTVZ7ND66A6N5PYJ \
                     --cloud-api-secret xxxxxxxxxxxxxxxxxxxxxxxxxxx \
                     --env t39219 \
                     --cluster-id lkc-v1nyz
```
## Output

The script will display a table with the topic names and their corresponding sizes in bytes. It will also display the total number of requested topics and the total retained bytes in MBytes. If the `--topics` argument is not provided, the script will print the size for all topics in the cluster.

Example output:
![Example Output](Screenshot_2023-05-03_060837.png) 




