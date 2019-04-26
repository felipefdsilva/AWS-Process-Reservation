#Title: Resizes disk by creating a greater volume from a snapshot
#Autor: Felipe Ferreira
#Data: 25/04/2019

import sys
import boto3

if (len(sys.argv) != 3):
    print ("Please, provide the volume id to be resized and the new size")
    print ("Usage: ", sys.argv[0], "<vol-...> <size-GB>")
    sys.exit(1)#if the number of arguments ir wrong, the program closes

target_volume_id=sys.argv[1] #EBS ID da instancia Automacoes (10GB)
new_size=int(sys.argv[2])

client = boto3.client('ec2') #configurando o serviço

#Criando um snapshot
print ("Creating Snapshot")

snapshot_data = client.create_snapshot(
    Description='teste felipe - create snapshot',
    VolumeId=target_volume_id, 
    TagSpecifications=[
        {
            'ResourceType': 'snapshot',
            'Tags': [
                {
                    'Key': 'name',
                    'Value': 'snapshot-teste'
                },
            ]
        },
    ],
    DryRun=False
)
client.get_waiter('snapshot_completed').wait(SnapshotIds=[snapshot_data["SnapshotId"]])

print("Snapshot " + snapshot_data["SnapshotId"] + "is ready")

#Descrevendo o volume o qual se deseja aumentar
print ("Getting info about the volume")

target_volume_data = client.describe_volumes(
    VolumeIds=[
        target_volume_id,
    ],
    DryRun=False,
)

#Criando um volume a partir do snapshot criado acima
print ('Creating new volume')

new_volume = client.create_volume (
    AvailabilityZone=target_volume_data['Volumes'][0]['AvailabilityZone'],
    Encrypted=False,
    #Iops=100,
    Size=new_size,
    SnapshotId=snapshot_data["SnapshotId"],
    VolumeType=target_volume_data['Volumes'][0]['VolumeType'],
    DryRun=False,
    TagSpecifications=[
        {
            'ResourceType': 'volume',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'teste-volume-felipe'
                },
            ]
        },
    ]
)

client.get_waiter('volume_available').wait(VolumeIds=[new_volume['VolumeId']])#waits the volume to be avaiable

print("New volume " + new_volume['VolumeId'] + " is ready")

# Stoping the instance
print ("Stoping Instance")
target_instance_id = target_volume_data['Volumes'][0]['Attachments'][0]['InstanceId'] #gets the volume attached instance ID
client.stop_instances(InstanceIds=[target_instance_id]) #requests the instance to stop
waiter=client.get_waiter('instance_stopped').wait(InstanceIds=[target_instance_id]) #wait until instance is stopped
print ("Instance " + target_instance_id + "successfully stopped")

#Detaching target volume from instance
print ("Detaching old volume")
target_instance_id = target_volume_data['Volumes'][0]['Attachments'][0]['InstanceId'] #gets the volume attached instance ID

response = client.detach_volume (
    Device=target_volume_data['Volumes'][0]['Attachments'][0]['Device'],
    Force=False,
    InstanceId=target_instance_id,
    VolumeId=target_volume_id,
    DryRun=False
)
waiter = client.get_waiter('volume_available').wait(VolumeIds=[new_volume['VolumeId']])
print ("Successfully detached volume")

#Attaching new volume to instance
print ("Attaching new volume")
response = client.attach_volume(
    Device=target_volume_data['Volumes'][0]['Attachments'][0]['Device'],
    InstanceId=target_instance_id,
    VolumeId=new_volume['VolumeId'],
    DryRun=False
)
waiter = client.get_waiter('volume_in_use').wait(VolumeIds=[new_volume['VolumeId']])
print ("Successfully atached new volume")

#Starting Instance
print ("Starting instance")
client.start_instances(InstanceIds=[target_instance_id]) #requests the instance to start
waiter=client.get_waiter('instance_running').wait(InstanceIds=[target_instance_id]) #wait until instance is stopped
print ("Instance " + target_instance_id + "successfully started")
