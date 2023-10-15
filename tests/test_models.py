"""
Test cases for Recommendation Model

Test cases can be run with:
    green
    coverage report -m
    
"""

import os
import logging
import unittest
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
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
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
        )
        self.assertTrue(recommendation is not None)
        self.assertEqual(recommendation.id, None)
        self.assertEqual(recommendation.source_item_id, 123)
        self.assertEqual(recommendation.target_item_id, 456)
        self.assertEqual(recommendation.recommendation_type, RecommendationType.UP_SELL)
        self.assertEqual(recommendation.recommendation_weight, 0.8)
        self.assertEqual(recommendation.status, RecommendationStatus.VALID)
        recommendation = Recommendation(
            source_item_id=123,
            target_item_id=456,
            recommendation_type=RecommendationType.CROSS_SELL,
            recommendation_weight=0.7,
            status=RecommendationStatus.DEPRECATED,
        )
        self.assertEqual(
            recommendation.recommendation_type, RecommendationType.CROSS_SELL
        )
        self.assertEqual(recommendation.recommendation_weight, 0.7)
        self.assertEqual(recommendation.status, RecommendationStatus.DEPRECATED)

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

    # def test_read_a_recommendation_by_source_item_id(self):
    #     """It should Read a Recommendation by id"""
    #     recommendation = RecommendationFactory()
    #     logging.debug(recommendation)
    #     recommendation.source_item_id = None
    #     recommendation.create()
    #     self.assertIsNotNone(recommendation.source_item_id)
    #     # Fetch it back
    #     found_recommendation = Recommendation.find_by_source_item_id(recommendation.id)

    #     self.assertTrue(recommendation is not None)
    #     self.assertEqual(found_recommendation.id, recommendation.id)
    #     self.assertEqual(
    #         found_recommendation.source_item_id, recommendation.source_item_id
    #     )
    #     self.assertEqual(
    #         found_recommendation.target_item_id, recommendation.target_item_id
    #     )
    #     self.assertEqual(
    #         found_recommendation.recommendation_type, recommendation.recommendation_type
    #     )
    #     self.assertEqual(
    #         found_recommendation.recommendation_weight,
    #         recommendation.recommendation_weight,
    #     )
    #     self.assertEqual(found_recommendation.status, recommendation.status)

    def test_update_recommendation_target_item_id(self):
        '''create and update recommendation target_item_id, '''
        recommendation = Recommendation(
            source_item_id=123,
            target_item_id=456,
            recommendation_type=RecommendationType.UP_SELL,
            recommendation_weight=0.8,
            status=RecommendationStatus.VALID,
        )
        recommendation.update({'source_item_id': 789, 'recommendation_weight': 0.2})
        self.assertEqual(recommendation.source_item_id, 789)
        self.assertEqual(recommendation.recommendation_weight, 0.2)
        
