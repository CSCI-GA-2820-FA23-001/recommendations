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

    def test_get_recommendation(self):
        """It should Get a recommendation by its id"""
        # get the id of a recommendation
        test_recommendation = self._create_recommendations(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["id"], test_recommendation.id)

    # def test_get_pet_list(self):
    #     """It should Get a list of Pets"""
    #     self._create_pets(5)
    #     response = self.client.get(BASE_URL)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     data = response.get_json()
    #     self.assertEqual(len(data), 5)

    # def test_get_pet_not_found(self):
    #     """It should not Get a Pet thats not found"""
    #     response = self.client.get(f"{BASE_URL}/0")
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    #     data = response.get_json()
    #     logging.debug("Response data = %s", data)
    #     self.assertIn("was not found", data["message"])

    # def test_create_pet(self):
    #     """It should Create a new Pet"""
    #     test_pet = PetFactory()
    #     logging.debug("Test Pet: %s", test_pet.serialize())
    #     response = self.client.post(BASE_URL, json=test_pet.serialize())
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #     # Make sure location header is set
    #     location = response.headers.get("Location", None)
    #     self.assertIsNotNone(location)

    #     # Check the data is correct
    #     new_pet = response.get_json()
    #     self.assertEqual(new_pet["name"], test_pet.name)
    #     self.assertEqual(new_pet["category"], test_pet.category)
    #     self.assertEqual(new_pet["available"], test_pet.available)
    #     self.assertEqual(new_pet["gender"], test_pet.gender.name)

    #     # Check that the location header was correct
    #     response = self.client.get(location)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     new_pet = response.get_json()
    #     self.assertEqual(new_pet["name"], test_pet.name)
    #     self.assertEqual(new_pet["category"], test_pet.category)
    #     self.assertEqual(new_pet["available"], test_pet.available)
    #     self.assertEqual(new_pet["gender"], test_pet.gender.name)

    # def test_create_recommendations(self):
    #     """Recommendation should be created via POST"""
    #     response = self.client.post(BASE_URL, json={})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     data = response.get_json()
    #     self.assertEqual(data["status"], 200)

    def test_update_recommendation(self):
        """Recommendation should be updated via PUT"""
        recommendations = self._create_recommendations(5)
        test_id = recommendations[2].id
        test_weight = recommendations[2].recommendation_weight
        changed_weight = max(test_weight + 0.01, 1)
        response = self.client.put(
            f"{BASE_URL}/{test_id}",
            json={"recommendation_weight": changed_weight},
        )
        data = response.get_json()
        self.assertTrue(hasattr(data, "recommendation_weight"))
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

    def test_create_pet_no_content_type(self):
        """It should not Create a Recommendation with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # def test_create_pet_wrong_content_type(self):
    #     """It should not Create a Pet with the wrong content type"""
    #     response = self.client.post(BASE_URL, data="hello", content_type="text/html")
    #     self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # def test_create_pet_bad_available(self):
    #     """It should not Create a Pet with bad available data"""
    #     test_pet = PetFactory()
    #     logging.debug(test_pet)
    #     # change available to a string
    #     test_pet.available = "true"
    #     response = self.client.post(BASE_URL, json=test_pet.serialize())
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_create_pet_bad_gender(self):
    #     """It should not Create a Pet with bad gender data"""
    #     pet = PetFactory()
    #     logging.debug(pet)
    #     # change gender to a bad string
    #     test_pet = pet.serialize()
    #     test_pet["gender"] = "male"  # wrong case
    #     response = self.client.post(BASE_URL, json=test_pet)
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    #     def test_get_
    # @app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
    # def method_not_supported(error):
    #     """Handles unsupported HTTP methods with 405_METHOD_NOT_SUPPORTED"""
    #     message = str(error)
    #     app.logger.warning(message)
    #     return (
    #         jsonify(
    #             status=status.HTTP_405_METHOD_NOT_ALLOWED,
    #             error="Method not Allowed",
    #             message=message,
    #         ),
    #         status.HTTP_405_METHOD_NOT_ALLOWED,
    #     )

    def test_delete_to_recommendations(self):
        """It should return 405 when sending DELETE to /recommendations"""
        response = self.client.delete(BASE_URL)
        self.assertEqual(response.status_code, 405)

    ######################################################################
    #  T E S T   A C T I O N S
    ######################################################################

    # def test_purchase_a_pet(self):
    #     """It should Purchase a Pet"""
    #     pets = self._create_pets(10)
    #     available_pets = [pet for pet in pets if pet.available is True]
    #     pet = available_pets[0]
    #     response = self.client.put(f"{BASE_URL}/{pet.id}/purchase")
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     response = self.client.get(f"{BASE_URL}/{pet.id}")
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     data = response.get_json()
    #     logging.debug("Response data: %s", data)
    #     self.assertEqual(data["available"], False)

    # def test_purchase_not_available(self):
    #     """It should not Purchase a Pet that is not available"""
    #     pets = self._create_pets(10)
    #     unavailable_pets = [pet for pet in pets if pet.available is False]
    #     pet = unavailable_pets[0]
    #     response = self.client.put(f"{BASE_URL}/{pet.id}/purchase")
    #     self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
