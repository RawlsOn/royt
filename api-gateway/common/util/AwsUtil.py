from django.conf import settings
from common.util.romsg import rp

import io, time, os, glob, pprint, json, re, shutil, ntpath, sys
pp = pprint.PrettyPrinter(indent=2) # pp.pprint()

from datetime import datetime, date, timedelta
# from django.utils import timezone
from pytz import timezone
from common.util.logger import RoLogger
from common.util.ProgressWatcher import ProgressWatcher
logger = RoLogger()

import boto3

class AwsUtil(object):

    def __init__(self, args={}):
        self.args = args
        self.prepare()

    def prepare(self):
        print('prepare...')
        print('load boto3...')

        regions = [
            # 'ap-northeast-2', # 얘는 뺀다. 상용서버가 돌고 있으니
            'us-east-1',
            'us-east-2',
            # 'us-west-1',
            'us-west-2',
            'af-south-1',
            'ap-east-1',
            'ap-south-2',
            'ap-southeast-3',
            'ap-southeast-4',
            'ap-south-1',
            'ap-northeast-3',
            'ap-southeast-1',
            # 'ap-northeast-2',
            'ap-southeast-2',
            'ap-northeast-1',
            'ca-central-1',
            'eu-central-1',
            'eu-west-1',
            'eu-west-2',
            'eu-south-1',
            'eu-west-3',
            'eu-south-2',
            'eu-north-1',
            'eu-central-2',
            'il-central-1',
            'me-south-1',
            'me-central-1',
            'sa-east-1',
        ]
        self.regions = regions # 외부에서 쓰기 위함
        # profile_name = 'ro-dev'
        # boto3.setup_default_session(profile_name= profile_name)
        # self.session = boto3.session.Session(profile_name= profile_name)
        self.clients = {}
        for region in regions:
            print('load region... %s' % region)
            self.clients[region] = boto3.client(
                'ec2',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name= region
            )

    def stop_instance(self, region, instance_id):
        try:
            return self.clients[region].stop_instances(InstanceIds=[instance_id])
        except Exception as e:
            rp(str(e), msg_type='error')
            raise e

    def terminate_instance(self, region, instance_id):
        try:
            return self.clients[region].terminate_instances(InstanceIds=[instance_id])
        except Exception as e:
            rp(str(e), msg_type='error')
            raise e

    def start_instance(self, region, instance_id):
        return self.clients[region].start_instances(InstanceIds=[instance_id])


    def describe_instance(self, region, instance_id):
        raw_ret = self.clients[region].describe_instances(InstanceIds=[instance_id])

        inst = raw_ret['Reservations'][0]['Instances'][0]

        datum = {}
        # pp.pprint(inst)
        datum['instanceId'] = inst['InstanceId']
        datum['state'] = inst['State']['Name']
        datum['name'] = inst['Tags'][0]['Value']
        datum['launch_time'] = (inst['LaunchTime'].astimezone(timezone("Asia/Seoul")))

        return datum

    def reboot_instance(self, region, instance_id):
        return self.clients[region].reboot_instances(InstanceIds=[instance_id])

    def describe_all_instances(self):
        print('describe_all_instances')
        ret = {}
        for region, client in self.clients.items():
            print('describe region: %s' % region)
            ret[region] = client.describe_instances()
        return ret

    def groom_described_instances(self, resp):
        final = []
        for region, result in resp.items():
            for r in result['Reservations']:
                for i in r['Instances']:
                    ret = {
                        'region': region,
                        'instanceId': i['InstanceId'],
                        'state': i['State']['Name'],
                        'ip': i.get('PublicIpAddress', ''),
                        'launch_time': i['LaunchTime'].astimezone(timezone("Asia/Seoul")),
                        'key_name': i.get('KeyName', ''),
                    }
                    final.append(ret)
        return final











    def describe_instances(self, region, instance_ids):
        raw_ret = self.clients[region].describe_instances(InstanceIds=instance_ids)
        ret = []
        # ret['raw'] = raw_ret
        for res in raw_ret['Reservations']:
            inst = res['Instances'][0]
            datum = {}
            # pp.pprint(inst)
            datum['instanceId'] = inst['InstanceId']
            datum['state'] = inst['State']['Name']
            datum['name'] = inst['Tags'][0]['Value']
            datum['launch_time'] = (inst['LaunchTime'].astimezone(timezone.Seoul))
            ret.append(datum)

        return ret







    def create_a_image(self, base_instance_id, ami_name):
        print('create_a_image')

        return self.ec2_client.create_image(
            InstanceId= base_instance_id,
            NoReboot= True,
            Name= ami_name
        )

    def create_a_instance_from_image(self, image_id, instance_type, name):

        resp = self.ec2.create_instances(
            ImageId=image_id,
            MinCount=1,
            MaxCount=1,
            InstanceType= instance_type,
            SecurityGroupIds= [ settings.AWS_SECURITY_GROUP_ID ],
            Monitoring= { 'Enabled': True },
            Placement= { 'AvailabilityZone': settings.AWS_AVAILABILITY_ZONE },
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': name}]
            }]
        )
        for instance in resp:
            return instance

    def create_instances_from_image(self, image_id, instance_type, name, qty):

        resp = self.ec2.create_instances(
            ImageId=image_id,
            MinCount=1,
            MaxCount=qty,
            InstanceType= instance_type,
            SecurityGroupIds= [ settings.AWS_SECURITY_GROUP_ID ],
            Monitoring= { 'Enabled': True },
            Placement= { 'AvailabilityZone': settings.AWS_AVAILABILITY_ZONE },
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': name}]
            }]
        )
        ret = []
        for instance in resp:
            ret.append(instance.id)
        return ret

    def get_instance_public_dns(self, instance_id):
        while True:
            resp = self.ec2_client.describe_instances(
                InstanceIds= [instance_id]
            )
            instances = resp["Reservations"][0]['Instances']
            states = [x['State']['Name'] for x in instances]
            print(states)
            if all(x == 'running' for x in states):
                return instances[0]['PublicDnsName']
            logger.INFO('wait for running instances.. sleep for 5 seconds...')
            time.sleep(5)

    def wait_for_image_creation(self, image_id):
        while True:
            image_status = self.ec2_client.describe_images(
                ImageIds= [image_id]
            )
            state = image_status['Images'][0]['State']
            print('status: ' + state)
            if state == 'available':
                break
            logger.INFO('wait for available images.. sleep for 5 seconds...')
            time.sleep(5)


    def get_instances_of_load_balancer(self, names= []):
        resp = self.elbv2_client.describe_target_health(
            TargetGroupArn= settings.AWS_LB_TARGET_ARN
        )
        ret = []
        for instance in resp['TargetHealthDescriptions']:
            instance_id = instance['Target']['Id']
            ret.append(instance_id)
        return ret

    def get_healthy_instances_of_load_balancer(self, names= []):
        resp = self.elbv2_client.describe_target_health(
            TargetGroupArn= settings.AWS_LB_TARGET_ARN
        )
        ret = []
        for instance in resp['TargetHealthDescriptions']:
            if instance['TargetHealth']['State'] == 'healthy':
                ret.append(instance['Target']['Id'])
        return ret

    def wait_for_instances_creation(self, instance_ids):
        print('wait_for_instances_creation')
        while True:
            resp = self.ec2_client.describe_instances(
                InstanceIds= instance_ids
            )
            # print(resp)
            states = [x['State']['Name'] for x in resp["Reservations"][0]['Instances']]
            print(states)
            if all(x == 'running' for x in states):
                break
            logger.INFO('sleep for 5 seconds...')
            time.sleep(5)

    def add_to_lb_targets(self, instance_ids):
        targets = [{'Id': iid} for iid in instance_ids]
        print('add_to_lb_targets', targets)
        self.elbv2_client.register_targets(
            TargetGroupArn= settings.AWS_LB_TARGET_ARN,
            Targets=targets
        )

    def is_every_instance_healthy_in_lb(self):
        print('check if every instance is healthy in lb')
        resp = self.elbv2_client.describe_target_health(
            TargetGroupArn= settings.AWS_LB_TARGET_ARN
        )
        states = list(filter(lambda x: x != 'unused', [x['TargetHealth']['State'] for x in resp['TargetHealthDescriptions']]))
        print(states)
        if all(x == 'healthy' for x in states):
            return True
        return False

    def wait_until_every_intances_healthy_in_lb(self):
        count = 0
        while True:
            count += 1
            resp = self.elbv2_client.describe_target_health(
                TargetGroupArn= settings.AWS_LB_TARGET_ARN
            )
            states = list(filter(lambda x: x != 'unused', [x['TargetHealth']['State'] for x in resp['TargetHealthDescriptions']]))
            print(count, states)
            if all(x == 'healthy' for x in states):
                break
            logger.INFO('sleep for 5 seconds...')
            time.sleep(5)

            if count > 100: # 500초 기다린다
                print('Some of instances are not healthy.')
                break


    def remove_instances(self, instances_to_remove):
        print('remove_instances: ', instances_to_remove)
        self.ec2.instances.filter(InstanceIds= instances_to_remove).stop()
        self.ec2.instances.filter(InstanceIds= instances_to_remove).terminate()

    def stop_instances(self, instances_to_remove):
        print('stop_instances: ', instances_to_remove)
        try:
            self.ec2.instances.filter(InstanceIds= instances_to_remove).stop()
        except Exception as e:
            rp(str(e), msg_type='error')
            raise e

    def assert_instances_count_of_lb(self, count):
            resp = self.elbv2_client.describe_target_health(
                TargetGroupArn= settings.AWS_LB_TARGET_ARN
            )
            states = list(filter(lambda x: x != 'unused', [x['TargetHealth']['State'] for x in resp['TargetHealthDescriptions']]))
            print('assert', count, len(states))
            assert(count == len(states))

    def get_meta_data(self):
        try:
            return json.load(open("/run/cloud-init/instance-data.json"))
        except Exception as e:
            rp('No metadata. Maybe you are using docker...: ' + str(e))
            return None