"""
Recommendation Service

Each person needs to modify the routes they have created. Here is the template provided by the professor.

Paths:
------
GET /recommendations - Returns a list all of the Recommendations
GET /pets/{id} - Returns the Pet with a given id number
POST /recommendations - creates a new Recommendation record in the database
PUT /pets/{id} - updates a Pet record in the database
DELETE /pets/{id} - deletes a Pet record in the database

"""

from flask import jsonify, request, url_for, abort
from service.models import Recommendation
from service.common import status  # HTTP Status Codes
from . import app  # Import Flask application


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/healthcheck")
def healthcheck():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Recommendation Demo REST API Service",
            version="1.0",
            # paths=url_for("list_recommendations", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# LIST ALL PETS
######################################################################
# @app.route("/pets", methods=["GET"])
# def list_pets():
#     """Returns all of the Pets"""
#     app.logger.info("Request for pet list")
#     pets = []
#     category = request.args.get("category")
#     name = request.args.get("name")
#     if category:
#         pets = Pet.find_by_category(category)
#     elif name:
#         pets = Pet.find_by_name(name)
#     else:
#         pets = Pet.all()

#     results = [pet.serialize() for pet in pets]
#     app.logger.info("Returning %d pets", len(results))
#     return jsonify(results), status.HTTP_200_OK


######################################################################
# RETRIEVE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:id>", methods=["GET"])
def get_recommendations(id):
    """
    Retrieve a single Recommendation

    This endpoint will return a Recommendation based on it's id
    """
    app.logger.info("Request for recommendation with id: %s", id)
    recommendation = Recommendation.find(id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id '{id}' was not found.",
        )

    app.logger.info("Returning recommendation: %s", recommendation.id)
    # need a more explicit message

    return jsonify(recommendation.serialize()), status.HTTP_200_OK


@app.route("/recommendations/<int:source_item_id>", methods=["GET"])
def read_recommendations_by_source_type(source_item_id):
    """
    Read a single Recommendation based on the source product they select
    This endpoint will return a Recommendation based on it's id
    """
    app.logger.info(
        "Request for recommendation with source product: %s", source_item_id
    )
    recommendation = Recommendation.find_by_source_item_id(source_item_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with source product id '{source_item_id}' was not found.",
        )

    app.logger.info("Returning recommendation: %s", recommendation.source_item_id)

    return jsonify(recommendation.serialize()), status.HTTP_200_OK


######################################################################
# ADD A NEW RECOMMENDATION
######################################################################
@app.route("/recommendations", methods=["POST"])
def create_recommendations():
    """
    Creates a Recommendation
    This endpoint will create a Recommendation based the data in the body that is posted
    """
    app.logger.info("Request to create a recommendation")
    check_content_type("application/json")
    recommendation = Recommendation()
    recommendation.deserialize(request.get_json())
    recommendation.create()
    message = recommendation.serialize()
    location_url = url_for(
        "get_recommendations",
        id=recommendation.id,
        _external=True,
    )
    app.logger.info("Recommendation with ID [%s] created.", recommendation.id)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# UPDATE AN EXISTING PET
######################################################################
# @app.route("/pets/<int:pet_id>", methods=["PUT"])
# def update_pets(pet_id):
#     """
#     Update a Pet

#     This endpoint will update a Pet based the body that is posted
#     """
#     app.logger.info("Request to update pet with id: %s", pet_id)
#     check_content_type("application/json")

#     pet = Pet.find(pet_id)
#     if not pet:
#         abort(status.HTTP_404_NOT_FOUND, f"Pet with id '{pet_id}' was not found.")

#     pet.deserialize(request.get_json())
#     pet.id = pet_id
#     pet.update()

#     app.logger.info("Pet with ID [%s] updated.", pet.id)
#     return jsonify(pet.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A PET
######################################################################
# @app.route("/pets/<int:pet_id>", methods=["DELETE"])
# def delete_pets(pet_id):
#     """
#     Delete a Pet

#     This endpoint will delete a Pet based the id specified in the path
#     """
#     app.logger.info("Request to delete pet with id: %s", pet_id)
#     pet = Pet.find(pet_id)
#     if pet:
#         pet.delete()

#     app.logger.info("Pet with ID [%s] delete complete.", pet_id)
#     return "", status.HTTP_204_NO_CONTENT


######################################################################
# PURCHASE A PET
######################################################################
# @app.route("/pets/<int:pet_id>/purchase", methods=["PUT"])
# def purchase_pets(pet_id):
#     """Purchasing a Pet makes it unavailable"""
#     pet = Pet.find(pet_id)
#     if not pet:
#         abort(status.HTTP_404_NOT_FOUND, f"Pet with id '{pet_id}' was not found.")
#     if not pet.available:
#         abort(
#             status.HTTP_409_CONFLICT,
#             f"Pet with id '{pet_id}' is not available.",
#         )

#     # At this point you would execute code to purchase the pet
#     # For the moment, we will just set them to unavailable

#     pet.available = False
#     pet.update()

#     return pet.serialize(), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )