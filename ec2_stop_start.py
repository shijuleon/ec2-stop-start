import argparse
import boto3
import jmespath

def stop_start_ec2_instances(client, instance_ids):
  client.stop_instances(
    InstanceIds=instance_ids
  )

  waiter = client.get_waiter('instance_stopped')
  waiter.wait(
      InstanceIds=instance_ids
  )

  client.start_instances(
      InstanceIds=instance_ids
  )

  waiter = client.get_waiter('instance_running')
  waiter.wait(
      InstanceIds=instance_ids
  )

def check_instances_running(client, instance_ids):
  response = client.describe_instances(
    Filters=[
        {
            'Name': 'instance-state-name',
            'Values': [
                'running',
            ]
        },
    ],
    InstanceIds=instance_ids
  )

  running_instances = jmespath.search('Reservations[*].Instances[*].InstanceId[]', response)

  if running_instances != instance_ids:
    raise Exception(f"Running {running_instances} doesn't match given {instance_ids}")

def main():
  parser = argparse.ArgumentParser(description='Stop & start instance IDs')
  parser.add_argument('instance_ids', type=str, help='instance IDs to stop & start')
  args = parser.parse_args()

  instance_ids = args.instance_ids.split(',')
  endpoint_url = "http://localhost:4566"
  client = boto3.client('ec2', endpoint_url=endpoint_url, region_name='us-east-1')

  stop_start_ec2_instances(client, instance_ids)
  check_instances_running(client, instance_ids)
  
if __name__ == '__main__':
  main()
