#!/usr/bin/env python3
# Description: Validates product descriptions passed through input
# Author: Felipe Ferreira da Silva
# Date: 12/07/2019

class ParameterValidationException (Exception):
    pass

#Validation of product_description input parameter
def validate_platform (input_product_descriptions):
    
    #List with valid product descriptions
    product_description_list = open('product_description_list.txt').read().splitlines()

    for product_description in input_product_descriptions:
        valid_description = False

        for item in product_description_list:
            if (product_description == item):
                valid_description = True
                break

        if (valid_description == False):
            return False
    
    return True

#Intance waste parameter validation
def validate_waste (waste, instance_count):
    remaining = instance_count - waste

    if (remaining < 0):
        error = "Cannot detach {wasted} instances from a reservation with {instance_count} instances".\
            format(wasted=waste,instance_count=instance_count)

        raise ParameterValidationException (error)
    
    return remaining