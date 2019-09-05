import boto3
from sts import get_client

class OfferingException (Exception):
    pass

def get_exchange_offering(reservation_description, target_instance_type, target_platform):

    ec2 = get_client('ec2')

    #Listagem de ofertas
    offerings = ec2.describe_reserved_instances_offerings(
        Filters = [
            {
                'Name' : 'scope',
                'Values': [reservation_description['Scope']]
            },
        ],
        MinDuration = reservation_description['Duration'],
        MaxDuration = reservation_description['Duration'],
        InstanceType = target_instance_type,
        OfferingClass = reservation_description['OfferingClass'],
        ProductDescription = target_platform,
        InstanceTenancy = reservation_description['InstanceTenancy'],
        OfferingType = reservation_description['OfferingType']
    )['ReservedInstancesOfferings']

    number_of_offerings = len(offerings)

    if (number_of_offerings != 1):
        raise OfferingException("The search returned " + \
                str(number_of_offerings) + \
                "instance offering(s)\n" + \
                "The exchange can't be done automatically\n" + \
                "Exiting\n")

    return offerings[0]['ReservedInstancesOfferingId']