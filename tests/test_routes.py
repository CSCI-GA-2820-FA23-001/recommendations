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
# from urllib.parse import quote_plus
from service import app
from service.common import status
from service.models import (
    db,
    init_db,
    Recommendation,
    RecommendationStatus,
)
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
        self.assertIn(b"Recommendation Demo RESTful Service", response.data)

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/healthcheck")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["message"], "Healthy")

    def test_get_recommendation(self):
        """It should Get a recommendation by its id"""
        # get the id of a recommendation
        test_recommendation = self._create_recommendations(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["id"], test_recommendation.id)

    def test_get_recommendation_not_found(self):
        """It should not Get a Recommendation that's not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_create_recommendations(self):
        """Recommendation should be created via POST"""
        test_recommendation = RecommendationFactory()
        initial_data = test_recommendation.serialize()

        # POST the serialized recommendation data
        response = self.client.post(BASE_URL, json=initial_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check the returned data matches the posted data
        returned_data = response.get_json()
        self.assertEqual(
            returned_data["target_item_id"], initial_data["target_item_id"]
        )
        self.assertEqual(
            returned_data["source_item_id"], initial_data["source_item_id"]
        )
        self.assertEqual(
            returned_data["recommendation_type"], initial_data["recommendation_type"]
        )
        self.assertEqual(returned_data["status"], initial_data["status"])
        self.assertEqual(
            returned_data["number_of_likes"], initial_data["number_of_likes"]
        )
        self.assertEqual(
            returned_data["recommendation_weight"],
            initial_data["recommendation_weight"],
        )

        # Make sure the returned data has an ID assigned
        self.assertIsNotNone(returned_data["id"])

        # Ensure the recommendation is actually in the database
        response = self.client.get(f"{BASE_URL}/{returned_data['id']}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_recommendation(self):
        """Recommendation should be updated via PUT"""
        recommendations = self._create_recommendations(5)
        test_id = recommendations[2].id
        test_weight = recommendations[2].recommendation_weight
        changed_weight = 0.0114
        response = self.client.put(
            f"{BASE_URL}/{test_id}",
            json={
                "recommendation_weight": changed_weight,
                "recommendation_type": "CROSS_SELL",
            },
        )
        data = response.get_json()
        self.assertNotEqual(data["recommendation_weight"], test_weight)
        self.assertEqual(data["recommendation_weight"], changed_weight)
        self.assertEqual(data["recommendation_type"], "CROSS_SELL")
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

    def test_read_recommendations_by_source_item_id(self):
        """It should Get a list recommendations by its source product id"""
        recommendations = self._create_recommendations(5)
        test_source_item_id = recommendations[0].source_item_id
        category_recommendations = [
            recommendation
            for recommendation in recommendations
            if recommendation.source_item_id == test_source_item_id
        ]
        response = self.client.get(
            f"{BASE_URL}/source-product?source_item_id={test_source_item_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(category_recommendations))
        # check the data just to be sure
        for recommendation in data:
            self.assertEqual(recommendation["source_item_id"], test_source_item_id)

    def test_read_valid_recommendations_by_source_item_id(self):
        """It should get a list of valid recommendations by its source product id"""
        recommendations = self._create_recommendations(5)
        test_source_item_id = recommendations[0].source_item_id
        category_recommendations = [
            recommendation
            for recommendation in recommendations
            if recommendation.source_item_id == test_source_item_id
            and recommendation.status == RecommendationStatus.VALID
        ]
        response = self.client.get(
            f"{BASE_URL}/source-product?source_item_id={test_source_item_id}&status=valid"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(category_recommendations))
        # check the data just to be sure
        for recommendation in data:
            self.assertEqual(recommendation["source_item_id"], test_source_item_id)
            self.assertEqual(recommendation["status"], "VALID")

    def test_get_recommendation_list(self):
        """It should Get a list of Recommendations"""
        number = 3
        recommendations = self._create_recommendations(number)
        ids = []
        for i in range(number):
            ids.append(recommendations[i].id)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()["items"]
        self.assertEqual(len(data), number)
        for i in range(number):
            self.assertEqual(data[i]["id"], ids[i])

    def test_get_recommendation_paginate(self):
        """It should Get a list of Recommendations with pagination"""
        total_pages = 15
        for _ in range(total_pages - 1):
            rec = RecommendationFactory()
            rec.recommendation_type = "UNKNOWN"
            rec.create()
        test_recommendation = RecommendationFactory()
        test_recommendation.recommendation_type = "UP_SELL"
        test_recommendation.create()

        # should return all if page_size > total_pages
        response = self.client.get(f"{BASE_URL}?page-size=100")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()["items"]
        self.assertEqual(len(data), total_pages)
        # should only return the first 5
        response = self.client.get(f"{BASE_URL}?page-index=1&page-size=5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()["items"]
        self.assertEqual(len(data), 5)
        # should only return the last 5
        response = self.client.get(f"{BASE_URL}?page-index=2&page-size=10")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()["items"]
        self.assertEqual(len(data), 5)
        # filtering should only get back the one that we changed
        response = self.client.get(f"{BASE_URL}?page-index=1&page-size=10&type=UP_SELL")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()["items"]
        self.assertEqual(len(data), 1)

    def test_like_recommendation(self):
        """It should Like a Recommendation"""
        recommendations = self._create_recommendations(1)
        rec = recommendations[0]
        self.assertEqual(rec.number_of_likes, 0)
        response = self.client.put(f"{BASE_URL}/{rec.id}/like")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(f"{BASE_URL}/{rec.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        logging.debug("Response data: %s", data)
        self.assertEqual(data["number_of_likes"], 1)

    def test_deactivate_recommendation(self):
        """It should deactivate a Recommendation"""
        recommendations = self._create_recommendations(1)
        rec = recommendations[0]
        response = self.client.put(f"{BASE_URL}/{rec.id+1}/deactivation")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.put(f"{BASE_URL}/{rec.id}/deactivation")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        logging.debug("Response data: %s", data)
        self.assertEqual(data["status"], "DEPRECATED")

    def test_activate_recommendation(self):
        """It should deactivate a Recommendation"""
        recommendations = self._create_recommendations(2)
        rec = recommendations[0]
        response = self.client.put(f"{BASE_URL}/{rec.id}/activation?status=VALID")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        logging.debug("Response data: %s", data)
        self.assertEqual(data["status"], "VALID")

        rec = recommendations[1]
        response = self.client.put(
            f"{BASE_URL}/{rec.id}/activation?status=OUT_OF_STOCK"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        logging.debug("Response data: %s", data)
        self.assertEqual(data["status"], "OUT_OF_STOCK")

    def test_read_recommendations_by_type(self):
        """It should get a list recommendations by its recommendation type"""
        recommendations = self._create_recommendations(10)
        test_recommendation_type = recommendations[0].recommendation_type
        same_type_recommendations = [
            recommendation
            for recommendation in recommendations
            if recommendation.recommendation_type == test_recommendation_type
        ]
        response = self.client.get(f"{BASE_URL}?type={test_recommendation_type.name}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()["items"]
        self.assertEqual(len(data), len(same_type_recommendations))
        for recommendation in data:
            self.assertEqual(
                recommendation["recommendation_type"], test_recommendation_type.name
            )

    def test_read_recommendations_by_status(self):
        """It should get a list recommendations by its recommendation status"""
        recommendations = self._create_recommendations(10)
        test_recommendation_status = recommendations[0].status
        same_status_recommendations = [
            recommendation
            for recommendation in recommendations
            if recommendation.status == test_recommendation_status
        ]
        response = self.client.get(
            f"{BASE_URL}?status={test_recommendation_status.name}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()["items"]
        self.assertEqual(len(data), len(same_status_recommendations))
        for recommendation in data:
            self.assertEqual(recommendation["status"], test_recommendation_status.name)

    ######################################################################
    #  T E S T   S A D   P A T H S
    ######################################################################

    def test_create_recommendation_no_data(self):
        """It should not Create a Recommendation with missing data"""
        response = self.client.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # response_data = response.get_json()
        # message = response_data.get("message", "No message provided")
        # print("Error message:", message)

    def test_create_recommendation_no_content_type(self):
        """It should not Create a Recommendation with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_recommendation_wrong_content_type(self):
        """It should not Create a Recommendation with the wrong content type"""
        response = self.client.post(
            BASE_URL, data="wrong content", content_type="text/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_recommendation_bad_rating(self):
        """It should not Create a Recommendation with bad weight data"""
        test_recommendation = RecommendationFactory()
        logging.debug(test_recommendation)
        # change weight to a string
        test_recommendation.recommendation_weight = "0.7"
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_recommendation_bad_type(self):
        """It should not Create a Recommendation with bad recommendation type data"""
        recommendation = RecommendationFactory()
        # change recommendation type to a bad value
        test_recommendation = recommendation.serialize()
        test_recommendation[
            "recommendation_type"
        ] = "INVALID_TYPE"  # This value is not in the RecommendationType enumeration
        response = self.client.post(BASE_URL, json=test_recommendation)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_to_recommendations(self):
        """It should return 405 when sending DELETE to /recommendations"""
        response = self.client.delete(BASE_URL)
        self.assertEqual(response.status_code, 405)

    def test_read_recommendations_by_source_item_id_empty_query(self):
        """It should return 400 when sending with out source_item_id"""
        response = self.client.get(f"{BASE_URL}/source-product")
        self.assertEqual(response.status_code, 400)

    def test_filter_recommendation_bad_type(self):
        """It should return 400 when given bad recommendation type query string"""
        recommendation = RecommendationFactory()
        recommendation.create()
        response = self.client.get(f"{BASE_URL}?type=INVALID_TYPE")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recommendation_bad_status(self):
        """It should return 400 when given bad recommendation type query string"""
        recommendation = RecommendationFactory()
        recommendation.create()
        response = self.client.get(f"{BASE_URL}?status=INVALID_TYPE")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_like_recommendation_bad_id(self):
        """It should return 404 when sending PUT to /recommendations/rec_id/like"""
        recommendations = self._create_recommendations(1)
        rec = recommendations[0]
        self.assertEqual(rec.number_of_likes, 0)
        response = self.client.put(f"{BASE_URL}/{rec.id+1}/like")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("not found", data["message"])
        response = self.client.get(f"{BASE_URL}/{rec.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        logging.debug("Response data: %s", data)
        self.assertEqual(data["number_of_likes"], 0)

    def test_activate_recommendation_bad_status(self):
        """
        It should return 400 when sending PUT to /recommendations/rec_id/activation without valid query of status.
        It should return 404 if recommendation not found.
        """
        recommendations = self._create_recommendations(2)
        rec = recommendations[0]
        response = self.client.put(f"{BASE_URL}/{rec.id}/activation")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        rec = recommendations[1]
        response = self.client.put(f"{BASE_URL}/{rec.id}/activation?status=null")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.put(f"{BASE_URL}/{rec.id+1}/activation")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  T E S T   A C T I O N S
    ######################################################################

    # def test_purchase_not_available(self):
    #     """It should not Purchase a Pet that is not available"""
    #     pets = self._create_pets(10)
    #     unavailable_pets = [pet for pet in pets if pet.available is False]
    #     pet = unavailable_pets[0]
    #     response = self.client.put(f"{BASE_URL}/{pet.id}/purchase")
    #     self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
