######################################################################
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
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
Recommendation Steps

Steps file for Recommendation.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from behave import given

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204


@given("the following recommendations")
def step_impl(context):
    """Delete all Pets and load new ones"""

    # List all of the pets and delete them one by one
    rest_endpoint = f"{context.base_url}/recommendations"
    context.resp = requests.get(rest_endpoint)
    assert context.resp.status_code == HTTP_200_OK
    for rec in context.resp.json()["items"]:
        context.resp = requests.delete(f"{rest_endpoint}/{rec['id']}")
        assert context.resp.status_code == HTTP_204_NO_CONTENT

    # load the database with new pets
    for row in context.table:
        payload = {
            "source_item_id": int(row["source_item_id"]),
            "target_item_id": int(row["target_item_id"]),
            "recommendation_type": row["type"],
            "recommendation_weight": float(row["weight"]),
            "status": row["status"],
            "number_of_likes": int(row["number_of_likes"]),
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        assert context.resp.status_code == HTTP_201_CREATED
