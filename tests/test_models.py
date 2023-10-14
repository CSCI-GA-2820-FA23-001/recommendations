"""
Test cases for Recommendation Model

"""
import os
import logging
import unittest
from service.models import (
    Recommendation,
    DataValidationError,
    db,
    RecommendationStatus,
    RecommendationType,
)

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
        pass

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        pass

    def setUp(self):
        """This runs before each test"""
        db.drop_all()  # remove all data from previous tests
        db.create_all()  # create tables for our data models

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()  # clean up the session
        db.drop_all()  # tear down the database table

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_recommendation_old(self):
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
