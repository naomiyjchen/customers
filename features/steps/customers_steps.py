######################################################################
# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Customer Steps

Steps file for customers.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from behave import given
from compare import expect


@given('the following customers')
def step_impl(context):
    """ Delete all Customers and load new ones """
    # List all of the customers and delete them one by one
    rest_endpoint = f"{context.BASE_URL}/customers"
    assert(context.resp.status_code == HTTP_200_OK)
    expect(context.resp.status_code).to_equal(200)
    for customer in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{customer['id']}")
        assert(context.resp.status_code == HTTP_204_NO_CONTENT)

    # load the database with new customers
    for row in context.table:
        payload = {
            "address": row['address'], 
            "first_name": row['first_name'],
            "last_name": row['last_name'],
            "status": row['status'] in ['True', 'true', '1']
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        assert(context.resp.status_code == HTTP_201_CREATED)