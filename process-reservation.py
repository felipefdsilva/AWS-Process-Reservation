#!/usr/bin/env python3
# Description: Automatically modifies aws instance reservations
# Author: Felipe Ferreira da Silva
# Date: 27/05/2019

import boto3 #for aws api
import json #for pretty print
import sys #for argv

#This is the main function
#Will receive
"""
--original reservation ids, separated by commas
--list of instance count of each new reservation, separated by '-'
--target instance type
--max hourly price difference
"""
