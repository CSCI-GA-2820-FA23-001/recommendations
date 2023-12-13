"""
Test cases for Recommendation Model

Test cases can be run with:
    green
    coverage report -m

"""

import os
import logging
import unittest
import random
from datetime import datetime
from werkzeug.exceptions import NotFound

from service.models import (
    Recommendation,
    DataValidationError,
    db,
    RecommendationType,
    RecommendationStatus,
)

from service import app

from tests.factories import RecommendationFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  Recommendation   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods


class TestRecommendation(unittest.TestCase):
    """Test Cases for Recommendation Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Recommendation.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Recommendation).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()  # clean up the session

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_recommendation(self):
        """Create a recommendation and assert that it exists"""
        recommendation = Recommendation(
            source_item_id=123,
            target_item_id=456,
            recommendation_type=RecommendationType.UP_SELL,
            recommendation_weight=0.8,
            status=RecommendationStatus.VALID,
            number_of_likes=0,
        )
        self.assertTrue(recommendation is not None)
        self.assertEqual(recommendation.id, None)
        self.assertEqual(recommendation.source_item_id, 123)
        self.assertEqual(recommendation.target_item_id, 456)
        self.assertEqual(recommendation.recommendation_type, RecommendationType.UP_SELL)
        self.assertEqual(recommendation.recommendation_weight, 0.8)
        self.assertEqual(recommendation.status, RecommendationStatus.VALID)
        self.assertEqual(recommendation.number_of_likes, 0)
        recommendation = Recommendation(
            source_item_id=123,
            target_item_id=456,
            recommendation_type=RecommendationType.CROSS_SELL,
            recommendation_weight=0.7,
            status=RecommendationStatus.DEPRECATED,
            number_of_likes=0,
        )
        self.assertEqual(
            recommendation.recommendation_type, RecommendationType.CROSS_SELL
        )
        self.assertEqual(recommendation.recommendation_weight, 0.7)
        self.assertEqual(recommendation.status, RecommendationStatus.DEPRECATED)

    def test_add_a_recommendation(self):
        """It should Create a recommendation and add it to the database"""
        # Use RecommendationFactory to create a recommendation
        recommendation = RecommendationFactory()

        self.assertTrue(recommendation is not None)
        recommendation.create()

        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(recommendation.id)
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 1)

    def test_read_a_recommendation_by_id(self):
        """It should Read a Recommendation by id"""
        recommendation = RecommendationFactory()
        logging.debug(recommendation)
        recommendation.id = None
        recommendation.create()
        self.assertIsNotNone(recommendation.id)
        # Fetch it back
        found_recommendation = Recommendation.find(recommendation.id)

        self.assertTrue(recommendation is not None)
        self.assertEqual(found_recommendation.id, recommendation.id)
        self.assertEqual(
            found_recommendation.source_item_id, recommendation.source_item_id
        )
        self.assertEqual(
            found_recommendation.target_item_id, recommendation.target_item_id
        )
        self.assertEqual(
            found_recommendation.recommendation_type, recommendation.recommendation_type
        )
        self.assertEqual(
            found_recommendation.recommendation_weight,
            recommendation.recommendation_weight,
        )
        self.assertEqual(found_recommendation.status, recommendation.status)

    def test_create_recommendation_raise_error(self):
        """It should raise DataValidationError if required field is not included or wrong type"""
        recommendation = Recommendation(
            source_item_id=123,
            recommendation_type=RecommendationType.UP_SELL,
            recommendation_weight=0.8,
            status=RecommendationStatus.VALID,
        )
        self.assertRaises(DataValidationError, recommendation.create)

    def test_find_by_source_item_id_with_sorting(self):
        """It should find recommendations by source product id and sort them by recommendation weight in both orders"""
        # Create recommendations with varying weights and the same source_item_id
        source_item_id = 100  # Example source item id
        weights = [0.1 * i for i in range(1, 11)]  # Example weights: 0.1, 0.2, ..., 1.0
        for weight in weights:
            recommendation = RecommendationFactory(
                source_item_id=source_item_id, recommendation_weight=weight
            )
            recommendation.create()

        # Test for descending order
        found_desc = Recommendation.find_by_source_item_id(source_item_id, "desc")
        found_weights_desc = [
            recommendation.recommendation_weight for recommendation in found_desc
        ]
        self.assertEqual(found_weights_desc, sorted(weights, reverse=True))

        # Test for ascending order
        found_asc = Recommendation.find_by_source_item_id(source_item_id, "asc")
        found_weights_asc = [
            recommendation.recommendation_weight for recommendation in found_asc
        ]
        self.assertEqual(found_weights_asc, sorted(weights))

        # Check if the number of recommendations is correct for both cases
        self.assertEqual(len(found_desc), len(weights))
        self.assertEqual(len(found_asc), len(weights))

        # Check if each recommendation has the correct source_item_id
        for recommendation in found_desc + found_asc:
            self.assertEqual(recommendation.source_item_id, source_item_id)

    def test_update_recommendation_target_item_id(self):
        """create and update recommendation with some data"""
        recommendation = RecommendationFactory()
        recommendation.create()
        self.assertIsNotNone(recommendation.id)
        new_source_item_id = recommendation.source_item_id + 8
        recommendation.source_item_id = new_source_item_id
        original_id = recommendation.id
        recommendation.update()
        self.assertEqual(recommendation.id, original_id)
        self.assertEqual(recommendation.source_item_id, new_source_item_id)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].id, original_id)
        self.assertEqual(recommendations[0].source_item_id, new_source_item_id)

    def test_update_no_id(self):
        """It should not Update a Pet with no id"""
        recommendation = RecommendationFactory()
        logging.debug(recommendation)
        recommendation.id = None
        self.assertRaises(DataValidationError, recommendation.update)

    def test_delete_a_recommendation(self):
        """It should Delete a Recommendation"""
        recommendation = RecommendationFactory()
        recommendation.create()
        self.assertEqual(len(Recommendation.all()), 1)
        # delete the recommendation and make sure it isn't in the database
        recommendation.delete()
        self.assertEqual(len(Recommendation.all()), 0)

    def test_serialize_a_recommendation(self):
        """It should serialize a Recommendation"""
        recommendation = RecommendationFactory()
        data = recommendation.serialize()
        self.assertNotEqual(data, None)
        self.assertNotIn("id", data)
        self.assertIn("source_item_id", data)
        self.assertEqual(data["source_item_id"], recommendation.source_item_id)
        self.assertIn("target_item_id", data)
        self.assertEqual(data["target_item_id"], recommendation.target_item_id)
        self.assertIn("recommendation_type", data)
        self.assertEqual(
            data["recommendation_type"], recommendation.recommendation_type.name
        )
        self.assertIn("recommendation_weight", data)
        self.assertEqual(
            data["recommendation_weight"], recommendation.recommendation_weight
        )
        self.assertIn("status", data)
        self.assertEqual(data["status"], recommendation.status.name)
        self.assertNotIn("created_at", data)
        self.assertNotIn("updated_at", data)

    def test_deserialize_a_recommendation(self):
        """It should de-serialize a Recommendation"""
        data = RecommendationFactory().serialize()
        recommendation = Recommendation()
        recommendation.deserialize(data)
        self.assertNotEqual(recommendation, None)
        self.assertEqual(recommendation.id, None)
        self.assertEqual(data["source_item_id"], recommendation.source_item_id)
        self.assertEqual(data["target_item_id"], recommendation.target_item_id)
        self.assertEqual(
            data["recommendation_type"], recommendation.recommendation_type.name
        )
        self.assertEqual(
            data["recommendation_weight"], recommendation.recommendation_weight
        )
        self.assertEqual(data["status"], recommendation.status.name)
        self.assertEqual(recommendation.created_at, None)
        self.assertEqual(recommendation.updated_at, None)

    def test_deserialize_a_recommendation_with_id_and_datetime(self):
        """It should de-serialize a Recommendation"""
        data = RecommendationFactory().serialize()
        data["id"] = 188
        data["created_at"] = "2023-12-08T15:30:00"
        data["updated_at"] = "2024-11-08T15:30:00"
        recommendation = Recommendation()
        recommendation.deserialize(data)
        self.assertNotEqual(recommendation, None)
        self.assertEqual(recommendation.id, data["id"])
        self.assertEqual(data["source_item_id"], recommendation.source_item_id)
        self.assertEqual(data["target_item_id"], recommendation.target_item_id)
        self.assertEqual(
            data["recommendation_type"], recommendation.recommendation_type.name
        )
        self.assertEqual(
            data["recommendation_weight"], recommendation.recommendation_weight
        )
        self.assertEqual(data["status"], recommendation.status.name)
        self.assertEqual(
            recommendation.created_at, datetime.fromisoformat(data["created_at"])
        )
        self.assertEqual(
            recommendation.updated_at, datetime.fromisoformat(data["updated_at"])
        )

    def test_deserialize_missing_data(self):
        """It should not deserialize a Recommendation with missing data"""
        data = {"id": 1, "source_item_id": 8}
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_bad_source_item_id(self):
        """It should not deserialize a bad source_item_id"""
        test_recommendation = RecommendationFactory()
        data = test_recommendation.serialize()
        data["source_item_id"] = -88
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_bad_target_item_id(self):
        """It should not deserialize a bad target_item_id"""
        test_recommendation = RecommendationFactory()
        data = test_recommendation.serialize()
        data["target_item_id"] = "785"
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_bad_recommendation_weight(self):
        """It should not deserialize a bad recommendation_weight"""
        test_recommendation = RecommendationFactory()
        data = test_recommendation.serialize()
        data["recommendation_weight"] = 1.8
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_bad_status(self):
        """It should not deserialize a bad status"""
        test_recommendation = RecommendationFactory()
        data = test_recommendation.serialize()
        data["status"] = "male"  # wrong case
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)
        # with self.assertRaises(DataValidationError) as context:
        #     recommendation.deserialize(data)
        # print(f"Caught exception: {context.exception}")

    def test_find_or_404_found(self):
        """It should Find or return 404 not found"""
        recommendations = RecommendationFactory.create_batch(3)
        for recommendation in recommendations:
            recommendation.create()

        recommendation = Recommendation.find_or_404(recommendations[1].id)
        self.assertIsNot(recommendation, None)
        self.assertEqual(recommendation.id, recommendations[1].id)
        self.assertEqual(
            recommendations[1].source_item_id, recommendation.source_item_id
        )
        self.assertEqual(
            recommendations[1].target_item_id, recommendation.target_item_id
        )
        self.assertEqual(
            recommendations[1].recommendation_type, recommendation.recommendation_type
        )
        self.assertEqual(
            recommendations[1].recommendation_weight,
            recommendation.recommendation_weight,
        )
        self.assertEqual(recommendations[1].status, recommendation.status)
        self.assertEqual(
            recommendations[1].created_at,
            recommendation.created_at,
        )
        self.assertEqual(
            recommendations[1].updated_at,
            recommendation.updated_at,
        )

    def test_find_or_404_not_found(self):
        """It should return 404 not found"""
        self.assertRaises(NotFound, Recommendation.find_or_404, 0)

    def test_list_all_recommendations(self):
        """It should List all Recommendations in the database"""
        recs = Recommendation.all()
        self.assertEqual(recs, [])
        # Create 5 Recommendations
        for _ in range(5):
            rec = RecommendationFactory()
            rec.create()
        # See if we get back 5 recs
        recs = Recommendation.all()
        self.assertEqual(len(recs), 5)

    def test_paginate(self):
        """It should List Recommendations with given page index and page size"""
        # Create some test data
        for _ in range(14):
            rec = RecommendationFactory()
            rec.recommendation_type = "UNKNOWN"
            rec.create()

        recommendation = RecommendationFactory()
        recommendation.recommendation_type = "UP_SELL"
        recommendation.create()

        # Test pagination
        recommendations_page1 = Recommendation.paginate(page_index=1, page_size=5).items
        recommendations_page2 = Recommendation.paginate(
            page_index=2, page_size=10
        ).items
        self.assertEqual(len(recommendations_page1), 5)
        self.assertEqual(len(recommendations_page2), 5)

        # Test pagination with filter
        recommendations_page3 = Recommendation.paginate(
            page_index=1,
            page_size=100,
            rec_type=RecommendationType["UP_SELL"],
        ).items
        self.assertEqual(len(recommendations_page3), 1)
        recommendations_page3 = Recommendation.paginate(
            page_index=1,
            page_size=100,
            rec_type=RecommendationType["UNKNOWN"],
        ).items
        self.assertEqual(len(recommendations_page3), 14)

    def test_like_a_recommendation(self):
        """It should like the given recommendation"""
        rec = RecommendationFactory()
        rec.create()
        self.assertEqual(rec.number_of_likes, 0)
        rec.like()
        self.assertEqual(rec.number_of_likes, 1)

    def test_like_a_recommendation_raise_error(self):
        """Like recommendation with invalid datatype should raise error"""
        rec = RecommendationFactory()
        rec.create()
        self.assertEqual(rec.number_of_likes, 0)
        rec.number_of_likes = "string"
        self.assertRaises(DataValidationError, rec.like)

    def test_deactivate_a_recommendation(self):
        """It should deactivate the given recommendation"""
        rec = RecommendationFactory()
        rec.create()
        rec.deactivate()
        self.assertEqual(rec.status, RecommendationStatus.DEPRECATED)

    def test_activate_a_recommendation(self):
        """It should activate the given recommendation with certain status"""
        recommendations = RecommendationFactory.create_batch(10)
        activated_status = ["VALID", "OUT_OF_STOCK"]
        for recommendation in recommendations:
            recommendation.create()
            idx = random.choice([0, 1])
            recommendation.activate(activated_status[idx])
            self.assertNotEqual(recommendation.status, RecommendationStatus.DEPRECATED)

    def test_filter_all_by_status(self):
        """It should return all recommendations filtered by given status in the database"""
        recs = Recommendation.all()
        self.assertEqual(recs, [])
        # Create 10 Recommendations
        recommendations = RecommendationFactory.create_batch(10)
        for recommendation in recommendations:
            recommendation.create()
        status = recommendations[0].status
        count = len(
            [
                recommendation
                for recommendation in recommendations
                if recommendation.status == status
            ]
        )
        found = Recommendation.filter_all_by_status(status)
        self.assertEqual(found.count(), count)
        for recommendation in found:
            self.assertEqual(recommendation.status, status)

    def test_find_valid_by_source_item_id_with_sorting(self):
        """It should find valid recommendations by source product id and sort them by recommendation weight"""
        # Create a batch of recommendations
        recommendations = RecommendationFactory.create_batch(10)
        for recommendation in recommendations:
            recommendation.create()

        # Find recommendations for a specific source item id and status
        source_item_id = recommendations[0].source_item_id
        valid_recommendations = [
            recommendation
            for recommendation in recommendations
            if recommendation.source_item_id == source_item_id
            and recommendation.status == RecommendationStatus.VALID
        ]

        # Test for descending order (default)
        found_desc = Recommendation.find_valid_by_source_item_id(source_item_id, "desc")
        found_weights_desc = [rec.recommendation_weight for rec in found_desc]
        self.assertEqual(found_weights_desc, sorted(found_weights_desc, reverse=True))

        # Test for ascending order
        found_asc = Recommendation.find_valid_by_source_item_id(source_item_id, "asc")
        found_weights_asc = [rec.recommendation_weight for rec in found_asc]
        self.assertEqual(found_weights_asc, sorted(found_weights_asc))

        # Validate the number of recommendations and their properties
        self.assertEqual(len(found_desc), len(valid_recommendations))
        for recommendation in found_desc + found_asc:
            self.assertEqual(recommendation.source_item_id, source_item_id)
            self.assertEqual(recommendation.status, RecommendationStatus.VALID)

    def test_find_all_by_type(self):
        """It should return all recommendations filtered by given type in the database"""
        # Create 10 Recommendations
        recommendations = RecommendationFactory.create_batch(10)
        for recommendation in recommendations:
            recommendation.create()
        recommendation_type = recommendations[0].recommendation_type
        cnt = len(
            [
                recommendation
                for recommendation in recommendations
                if recommendation.recommendation_type == recommendation_type
            ]
        )
        found = Recommendation.find_by_recommendation_type(recommendation_type)
        self.assertEqual(found.count(), cnt)
        for recommendation in found:
            self.assertEqual(recommendation.recommendation_type, recommendation_type)

    def test_find_all_by_type_with_invalid_type(self):
        """It should not allow invalid recommendation types"""
        invalid_type_1 = "UP_SELL"
        self.assertRaises(
            AttributeError, Recommendation.find_by_recommendation_type, invalid_type_1
        )
        invalid_type_2 = 1
        self.assertRaises(
            AttributeError, Recommendation.find_by_recommendation_type, invalid_type_2
        )
