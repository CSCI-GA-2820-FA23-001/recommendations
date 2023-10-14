# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
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

"""
Test Factory to make fake objects for testing
"""
from datetime import datetime

import factory
from factory.fuzzy import FuzzyInteger, FuzzyChoice, FuzzyFloat, FuzzyDateTime
from service.models import Recommendation, RecommendationType, RecommendationStatus


class RecommendationFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Recommendation

    recommendation_id = factory.Sequence(lambda n: n)

    source_item_id = FuzzyInteger(1, 200)

    # generate a target_item_id different from source_item_id
    target_item_id = FuzzyInteger(source_item_id + 1, 300)

    recommendation_type = FuzzyChoice(
        choices=[
            RecommendationType.UNKNOWN,
            RecommendationType.UP_SELL,
            RecommendationType.CROSS_SELL,
            RecommendationType.ACCESSORY,
            RecommendationType.SUBSTITUTE,
            RecommendationType.COMPLEMENTARY,
        ]
    )

    recommendation_weight = FuzzyFloat(0, 1)

    status = FuzzyChoice(
        choices=[
            RecommendationStatus.UNKNOWN,
            RecommendationStatus.VALID,
            RecommendationStatus.OUT_OF_STOCK,
            RecommendationStatus.DEPRECATED,
        ]
    )

    created_at = FuzzyDateTime(datetime(2022, 1, 1), datetime(2023, 9, 14))

    updated_at = FuzzyDateTime(created_at, datetime(2023, 12, 31))
