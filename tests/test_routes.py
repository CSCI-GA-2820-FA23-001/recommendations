"""
Recommendation API Service Test Suite

Test cases can be run with the following:
  green
  coverage report -m
"""
import os
import logging
from unittest import TestCase

# from unittest.mock import MagicMock, patch
from urllib.parse import quote_plus
from service import app
from service.common import status
from service.models import db, init_db, Recommendation
from tests.factories import RecommendationFactory

# Disable all but critical errors during normal test run
# uncomment for debugging failing tests
# logging.disable(logging.CRITICAL)

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/recommendations"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestRecommendationServer(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        self.client = app.test_client()
        db.session.query(Recommendation).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    def _create_recommendations(self, count):
        """Factory method to create recommendations in bulk"""
        recommendations = []
        for _ in range(count):
            test_recommendation = RecommendationFactory()
            response = self.client.post(BASE_URL, json=test_recommendation.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test recommendation",
            )
            new_recommendation = response.get_json()
            test_recommendation.id = new_recommendation["id"]
            recommendations.append(test_recommendation)
        return recommendations

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], "Recommendation Demo REST API Service")

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/healthcheck")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["message"], "Healthy")

    def test_get_recommendations(self):
        """It should Get a recommendation by its id"""
        # get the id of a pet
        test_recommendation = self._create_recommendations(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["id"], test_recommendation.id)

    def test_read_recommendations_by_source_item_id(self):
        """It should Get a list recommendations by its source product id"""
        recommendations = self._create_recommendations(5)
        test_source_item_id = recommendations[0].source_item_id
        category_recommendations = [
            recommendation
            for recommendation in recommendations
            if recommendation.source_item_id == test_source_item_id
        ]
        response = self.client.get(f"{BASE_URL}/source_product_{test_source_item_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(category_recommendations))
        # check the data just to be sure
        for recommendation in data:
            self.assertEqual(recommendation["source_item_id"], test_source_item_id)

    # def test_create_recommendations(self):
    #     """Recommendation should be created via POST"""
    #     response = self.client.post(BASE_URL, json={})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     data = response.get_json()
    #     self.assertEqual(data["status"], 200)

    def test_update_recommendations(self):
        """Recommendation should be updated via PUT"""
        recommendations = self._create_recommendations(5)
        test_id = recommendations[2].id
        test_weight = recommendations[2].recommendation_weight
        changed_weight = max(test_weight + 0.01, 1)

        response = self.client.put(
            BASE_URL,
            json={"id": test_id, "data": {"recommendation_weight": changed_weight}},
        )
        data = response.get_json()
        self.assertNotEqual(data["recommendation_weight"], test_weight)
        self.assertEqual(data["recommendation_weight"], changed_weight)
        self.assertEqual(data["id"], test_id)

    def test_delete_recommendation(self):
        """It should Delete A Recommendation"""
        test_recommendation = self._create_recommendations(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_recommendation_list(self):
        """It should Get a list of Recommendations"""
        self._create_recommendations(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    ######################################################################
    #  T E S T   S A D   P A T H S
    ######################################################################

    ######################################################################
    #  T E S T   A C T I O N S
    ######################################################################
