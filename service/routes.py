"""
Recommendation Service

Paths:
------
GET /recommendations - Returns a list all of the Recommendations
GET /recommendations/{id} - Returns the Recommendation with a given id number
POST /recommendations - creates a new Recommendation record in the database
PUT /recommendations - updates a Recommendation record in the database
DELETE /recommendations/{id} - deletes a Recommendation record in the database

"""
from flask_restx import Resource, fields, reqparse
from service.models import Recommendation, RecommendationType, RecommendationStatus
from service.common import status  # HTTP Status Codes
from . import app, api  # Import Flask application


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health():
    """Health Status"""
    return {"status": "OK"}, status.HTTP_200_OK


######################################################################
# Configure the Root route before OpenAPI
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


# Define the model so that the docs reflect what can be sent
create_model = api.model(
    "Recommendation",
    {
        "source_item_id": fields.Integer(
            required=True, description="Source item id of the Recommendation"
        ),
        "target_item_id": fields.Integer(
            required=True, description="Target item id of the Recommendation"
        ),
        # pylint: disable=protected-access
        "recommendation_type": fields.String(
            enum=RecommendationType._member_names_,
            description="The type of the Recommendation",
        ),
        "recommendation_weight": fields.Float(
            required=True, description="The weight of the Recommendation"
        ),
        "status": fields.String(
            enum=RecommendationStatus._member_names_,
            description="The status of the Recommendation",
        ),
        "number_of_likes": fields.Integer(
            description="The number of likes of the Recommendation"
        ),
    },
)

recommendation_model = api.inherit(
    "RecommendationModel",
    create_model,
    {
        "id": fields.Integer(
            readOnly=True, description="The unique id assigned internally by service"
        ),
        "created_at": fields.DateTime(
            readOnly=True, description="The datetime the recommendation was created"
        ),
        "updated_at": fields.DateTime(
            readOnly=True, description="The datetime the recommendation was updated"
        ),
    },
)

# query string arguments
rec_args = reqparse.RequestParser()
rec_args.add_argument(
    "page-index",
    type=int,
    location="args",
    required=False,
    default=1,
    help="Page index for pagination",
)
rec_args.add_argument(
    "page-size",
    type=int,
    location="args",
    required=False,
    default=10,
    help="Number of items per page for pagination",
)
rec_args.add_argument(
    "type",
    type=str,
    location="args",
    required=False,
    default=None,
    help="Filter recommendations by type",
)
rec_args.add_argument(
    "status",
    type=str,
    location="args",
    required=False,
    default=None,
    help="Filter recommendations by status",
)
sp_args = reqparse.RequestParser()
sp_args.add_argument(
    "source_item_id",
    type=int,
    location="args",
    required=True,
    help="Source item id of the Recommendation",
)
sp_args.add_argument(
    "sort_order",
    type=str,
    location="args",
    required=False,
    default="desc",
    help="Sort recommendations by weight",
)
sp_args.add_argument(
    "status",
    type=str,
    location="args",
    required=False,
    default=None,
    help="Filter recommendations by status",
)



######################################################################
#  PATH: /recommendations/{id}
######################################################################
@api.route("/recommendations/<rec_id>")
@api.param("rec_id", "The Recommendation identifier")
class RecommendationResource(Resource):
    """
    RecommendationResource class

    Allows the manipulation of a single Recommendation
    GET /recommendations/{id} - Return a Recommendation with the id
    PUT /recommendations/{id} - Update a Recommendation with the id
    DELETE /recommendations/{id} -  Delete a Recommendation with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A Recommendation
    # ------------------------------------------------------------------
    @api.doc("get_recommendation")
    @api.response(404, "Recommendation not found")
    @api.marshal_with(recommendation_model)
    def get(self, rec_id):
        """
        Retrieve a single Recommendation

        This endpoint will return a Recommendation based on it's id
        """
        app.logger.info("Request to Retrieve a pet with id [%s]", rec_id)
        recommendation = Recommendation.find(rec_id)
        if not recommendation:
            abort(
                status.HTTP_404_NOT_FOUND,
                "404 Not Found",
            )
        return recommendation.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING Recommendation
    # ------------------------------------------------------------------
    @api.doc("update_recommendations")
    @api.response(404, "Recommendation not found")
    @api.response(400, "The posted Recommendation data was not valid")
    @api.expect(recommendation_model)
    @api.marshal_with(recommendation_model)
    def put(self, rec_id):
        """
        Update a Recommendation

        This endpoint will update a Recommendation based the body that is posted
        """
        app.logger.info("Request to Update a Recommendation with id [%s]", rec_id)
        try:
            rec_id = int(rec_id)
        except ValueError:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Recommendation with id '{rec_id}' was not found.",
            )
        recommendation = Recommendation.find(rec_id)
        if not recommendation:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Recommendation with id '{rec_id}' was not found.",
            )
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        recommendation.deserialize(data)
        recommendation.id = rec_id
        recommendation.update()
        return recommendation.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A Recommendation
    # ------------------------------------------------------------------
    @api.doc("delete_recommendations")
    @api.response(204, "Recommendation deleted")
    def delete(self, rec_id):
        """
        Delete a Recommendation

        This endpoint will delete a Recommendation based the id specified in the path
        """
        app.logger.info("Request to Delete a Recommendation with id [%s]", rec_id)
        recommendation = Recommendation.find(rec_id)
        if recommendation:
            recommendation.delete()
            app.logger.info("Recommendation with id [%s] was deleted", rec_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /recommendations
######################################################################
@api.route("/recommendations", strict_slashes=False)
class RecommendationCollection(Resource):
    """Handles all interactions with collections of Recommendations"""

    # ------------------------------------------------------------------
    # LIST ALL Recommendations
    # ------------------------------------------------------------------
    @api.doc("list_recommendations")
    @api.expect(rec_args, validate=True)
    def get(self):
        """Returns all of the Recommendations"""
        app.logger.info("Request to list Recommendations...")
        args = rec_args.parse_args()
        page_index = args["page-index"]
        page_size = args["page-size"]
        rec_type = args["type"]
        rec_status = args["status"]

        if rec_type is not None:
            app.logger.info("Find by recommendation type: %s", rec_type)
        if rec_status is not None:
            app.logger.info("Find by recommendation status: %s", rec_status)

        paginated_recommendations = Recommendation.paginate(
            page_index=page_index,
            page_size=page_size,
            rec_type=rec_type,
            rec_status=rec_status,
        )

        results = {
            "page": paginated_recommendations.page,
            "per_page": paginated_recommendations.per_page,
            "total": paginated_recommendations.total,
            "pages": paginated_recommendations.pages,
            "items": [
                recommendation.serialize()
                for recommendation in paginated_recommendations.items
            ],
        }
        app.logger.info("Returning %d recommendations", len(results["items"]))
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW RECOMMENDATION
    # ------------------------------------------------------------------
    @api.doc("create_recommendation")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_model)
    @api.marshal_with(recommendation_model, code=201)
    def post(self):
        """
        Creates a Recommendation
        This endpoint will create a Recommendation based the data in the body that is posted
        """
        app.logger.info("Request to Create a Recommendation")
        recommendation = Recommendation()
        app.logger.debug("Payload = %s", api.payload)
        recommendation.deserialize(api.payload)
        recommendation.create()
        app.logger.info("Recommendation with new id [%s] created!", recommendation.id)
        location_url = api.url_for(
            RecommendationResource, rec_id=recommendation.id, _external=True
        )
        return (
            recommendation.serialize(),
            status.HTTP_201_CREATED,
            {"Location": location_url},
        )


######################################################################
#  PATH: /recommendations/<int:recommendation_id>/like
######################################################################
@api.route("/recommendations/<int:rec_id>/like")
@api.param("rec_id", "The Recommendation identifier")
class LikeResource(Resource):
    """Like actions on a Recommendation"""

    @api.doc("like_recommendations")
    @api.response(404, "Recommendation not found")
    def put(self, rec_id):
        """
        Like a Recommendation

        This endpoint will like a Recommendation based the id specified in the path
        """
        app.logger.info("Request to Like a Pet")
        recommendation = Recommendation.find(rec_id)
        if not recommendation:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Recommendation with id [{rec_id}] was not found.",
            )
        recommendation.like()
        app.logger.info(
            "Recommendation with id [%s] has been liked!", recommendation.id
        )
        return recommendation.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /recommendations/source-product
######################################################################
@api.route("/recommendations/source-product", strict_slashes=False)
class ReadListResource(Resource):
    """Handles all interactions with collections of Recommendations with given source product"""
    @api.doc("read_recommendations_by_source_type")
    @api.expect(sp_args, validate=True)
    @api.response(400, "Source item ID is required")
    def get(self):
        """
        Read a list of recommendations based on the source product they select,
        with optional sorting by recommendation weight.
        """
        app.logger.info("Request for recommendations list based on source product")
        args = sp_args.parse_args()
        source_item_id = args["source_item_id"]
        sort_order = args["sort_order"]
        product_status = args["status"]

        if source_item_id is None:
            return {"error": "Source item ID is required"}, 400

        recommendations = []
        if product_status == "valid":
            # Assuming find_valid_by_source_item_id also needs to be updated for sorting
            recommendations = Recommendation.find_valid_by_source_item_id(
                source_item_id, sort_order
            )
        else:
            recommendations = Recommendation.find_by_source_item_id(
                source_item_id, sort_order
            )

        results = [recommendation.serialize() for recommendation in recommendations]
        app.logger.info("Returning %d recommendations", len(results))
        return results, status.HTTP_200_OK
######################################################################
#  PATH: /recommendations/<int:recommendation_id>/deactivation
######################################################################
@api.route("/recommendations/<int:recommendation_id>/deactivation")
@api.param("recommendation_id", "The Recommendation identifier")
class DeactivationResource(Resource):
    """Deactivate actions on a Recommendation"""

    @api.doc("deactivate_recommendation")
    @api.response(404, "Recommendation not found")
    def put(self, recommendation_id):
        """
        Deactivate a Recommendation
        """
        app.logger.info(
            "Request to deactivate recommendation with id: %s", recommendation_id
        )
        recommendation = Recommendation.find(recommendation_id)
        if not recommendation:
            abort(status.HTTP_404_NOT_FOUND, "recommendation not found")
        recommendation.deactivate()
        return recommendation.serialize(), status.HTTP_200_OK
######################################################################
#  PATH: /recommendations/<int:recommendation_id>/activation
######################################################################
@api.route("/recommendations/<int:recommendation_id>/activation")
@api.param("recommendation_id", "The Recommendation identifier")
class ActivationResource(Resource):
    """Activate actions on a Recommendation"""

    @api.doc("activate_recommendation")
    @api.expect(rec_args, validate=True)
    @api.response(404, "Recommendation not found")
    def put(self, recommendation_id):
        """
        Activate a Recommendation
        """
        app.logger.info("Request to activate recommendation with id: %s", recommendation_id)
        args = rec_args.parse_args()
        activated_status = args["status"]
        valid_status = ["VALID", "OUT_OF_STOCK"]
        recommendation = Recommendation.find(recommendation_id)
        if not recommendation:
            abort(status.HTTP_404_NOT_FOUND, "recommendation not found")
        if activated_status not in valid_status:
            abort(status.HTTP_400_BAD_REQUEST, "status for activation is required")
        recommendation.activate(activated_status)

        return recommendation.serialize(), status.HTTP_200_OK

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)


def init_db(dbname="recommendations"):
    """Initialize the model"""
    Recommendation.init_db(dbname)
