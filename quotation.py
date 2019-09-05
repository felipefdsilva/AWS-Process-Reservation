import boto3
from sts import get_client

class QuotationException(Exception):
    pass

def check_exchange_quote (reservation_id, offering_id, instance_count, max_price_difference):

    ec2 = get_client('ec2')

    #Quotating exchange
    exchange_quote = ec2.get_reserved_instances_exchange_quote(
        ReservedInstanceIds = [reservation_id],
        TargetConfigurations = [{'OfferingId': offering_id}]
    )
    #Checking price difference
    original_hourly_price = float(
        exchange_quote['ReservedInstanceValueSet'][0]['ReservationValue']['HourlyPrice']
    )
    target_hourly_price = float(
        exchange_quote['TargetConfigurationValueSet'][0]['ReservationValue']['HourlyPrice']
    )
    difference = target_hourly_price - original_hourly_price

    if (difference > max_price_difference):
        raise QuotationException("The exchange will not be done\n" + \
                "The target reservation hourly price is " + \
                str(target_hourly_price) + "\n" + \
                "The original reservation hourly price is " + \
                str(original_hourly_price) + "\n" + \
                "Exiting\n")

    #Checking instance count
    quotated_instance_count = \
        exchange_quote['TargetConfigurationValueSet'][0]['TargetConfiguration']['InstanceCount']

    if (quotated_instance_count != instance_count):
        raise QuotationException(
            "The instance count did not match\n" + \
            "Instance Count by quotation: " + str(quotated_instance_count) + "\n" + \
            "Instance Count Expected: " + str(instance_count) + "\n"
        )
                
    return exchange_quote