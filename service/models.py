"""
Models for Recommendation

All of the models are stored in this module
"""
from datetime import datetime
import logging
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


# Function to initialize the database
def init_db(app):
    """Initializes the SQLAlchemy app"""
    Recommendation.init_db(app)


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class RecommendationType(Enum):
    """Enumeration of recommendation type"""

    UNKNOWN = 0
    UP_SELL = 1
    CROSS_SELL = 2
    ACCESSORY = 3
    COMPLEMENTARY = 4
    SUBSTITUTE = 5


class RecommendationStatus(Enum):
    """Enumeration of recommendation status"""

    UNKNOWN = 0
    VALID = 1
    OUT_OF_STOCK = 2
    DEPRECATED = 3


# pylint: disable=too-many-instance-attributes
class Recommendation(db.Model):
    """
    Class that represents a Recommendation
    """

    app = None
    __tablename__ = "recommendation"

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    source_item_id = db.Column(db.Integer, nullable=False)
    target_item_id = db.Column(db.Integer, nullable=False)
    recommendation_type = db.Column(
        db.Enum(RecommendationType),
        nullable=False,
        server_default=(RecommendationType.UNKNOWN.name),
    )
    recommendation_weight = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(
        db.Enum(RecommendationStatus),
        nullable=False,
        server_default=RecommendationStatus.UNKNOWN.name,
    )
    number_of_likes = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    ##################################################
    # INSTANCE METHODS
    ##################################################

    # def __repr__(self):
    #     return f"<Recommendation with id=[{self.id}]>"

    def create(self):
        """
        Creates a Recommendation to the database
        """
        try:
            logger.info("Attempting to create Recommendation with ID %s", self.id)
            # id must be none to generate next primary key
            self.id = None  # pylint: disable=invalid-name
            self.created_at = None
            self.updated_at = None
            db.session.add(self)
            db.session.commit()
            logger.info("Successfully created Recommendation with ID %s", self.id)
        except Exception as error:
            logger.error("Error creating Recommendation: %s", error)
            db.session.rollback()
            raise DataValidationError(
                "Error creating Recommendation: " + str(error)
            ) from error

    def update(self):
        """
        Update a Recommendation to the database
        """
        logger.info("Updating %s", self.id)
        try:
            logger.info("Attempting to update Recommendation with ID %s", self.id)
            if not self.id:
                raise DataValidationError("Update called with empty ID field")
            db.session.commit()
            logger.info("Successfully updated Recommendation with ID %s", self.id)
        except Exception as error:
            logger.error("Error updating Recommendation: %s", error)
            db.session.rollback()
            raise DataValidationError(
                "Error updating Recommendation: " + str(error)
            ) from error

    def delete(self):
        """Removes a Recommendation from the data store"""
        logger.info("Deleting %s", self.id)
        db.session.delete(self)
        db.session.commit()

    def like(self):
        """
        Likes a Recommendation
        """
        logger.info("Liking %s", self.id)
        try:
            logger.info("Attempting to like Recommendation with ID %s", self.id)
            data = self.serialize()
            data["number_of_likes"] = data["number_of_likes"] + 1
            self.deserialize(data)
            db.session.commit()
            logger.info("Successfully liked Recommendation with ID %s", self.id)
        except Exception as error:
            logger.error("Error liking Recommendation: %s", error)
            db.session.rollback()
            raise DataValidationError(
                "Error liking Recommendation: " + str(error)
            ) from error

    def deactivate(self):
        """
        Deactivate a Recommendation
        """
        logger.info("Deactivating %s", self.id)
        logger.info("Attempting to deactivate Recommendation with ID %s", self.id)
        data = self.serialize()
        data["status"] = "DEPRECATED"
        self.deserialize(data)
        db.session.commit()
        logger.info("Successfully deactivated Recommendation with ID %s", self.id)

    def activate(self, status):
        """
        Activate a Recommendation
        """
        logger.info("Activating %s", self.id)
        logger.info("Attempting to activate Recommendation with ID %s", self.id)
        data = self.serialize()
        data["status"] = status
        self.deserialize(data)
        db.session.commit()
        logger.info("Successfully activated Recommendation with ID %s", self.id)

    def serialize(self):
        """Serializes a Recommendation into a dictionary"""
        recommendation = {
            "source_item_id": self.source_item_id,
            "target_item_id": self.target_item_id,
            "recommendation_type": self.recommendation_type.name,
            "recommendation_weight": self.recommendation_weight,
            "status": self.status.name,
            "number_of_likes": self.number_of_likes,
        }
        if self.id:
            recommendation["id"] = self.id
        if self.created_at:
            recommendation["created_at"] = self.created_at.isoformat()
        if self.updated_at:
            recommendation["updated_at"] = self.updated_at.isoformat()
        return recommendation

    def _deserialize_int_field(self, data, key):
        value = data.get(key)
        if isinstance(value, int) and value >= 0:
            return value
        raise DataValidationError(f"Invalid type or value for int [{key}]: {value}")

    def _deserialize_recommendation_weight(self, data):
        value = data.get("recommendation_weight")
        if isinstance(value, (int, float)) and 0 <= value <= 1:
            return value
        raise DataValidationError(
            f"Invalid type or value for recommendation weight: {value}"
        )

    def deserialize(self, data):
        """
        Deserializes a Recommendation from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        logger.info("deserialize(%s)", data)
        try:
            self.source_item_id = self._deserialize_int_field(data, "source_item_id")
            self.target_item_id = self._deserialize_int_field(data, "target_item_id")
            self.number_of_likes = self._deserialize_int_field(data, "number_of_likes")
            self.recommendation_weight = self._deserialize_recommendation_weight(data)
            if "recommendation_type" in data:
                self.recommendation_type = RecommendationType[
                    data["recommendation_type"].upper()
                ]
            if "status" in data:
                self.status = RecommendationStatus[data["status"].upper()]
        except KeyError as error:
            raise DataValidationError(
                "Invalid recommendation: missing or wrong enum value " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid recommendation: body of request contained bad or no data "
                + str(error)
            ) from error
        except AttributeError as error:
            raise DataValidationError(
                "Invalid recommendation: expected a dictionary, but got a string or other type "
                + str(error)
            ) from error
        # if there is no id and the data has one, assign it
        if not self.id and "id" in data:
            self.id = data["id"]
        if not self.created_at and "created_at" in data:
            self.created_at = datetime.fromisoformat(data["created_at"])
        if not self.updated_at and "updated_at" in data:
            self.updated_at = datetime.fromisoformat(data["updated_at"])
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def init_db(cls, app):
        """Initializes the database session"""
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """Returns all of the Recommendation in the database"""
        logger.info("Processing all Recommendation")

        return cls.query.all()

    @classmethod
    def paginate(cls, page_index=1, page_size=10, rec_type=None, rec_status=None):
        """Returns list of the Recommendation in the database,
        with optional pagination, filter rec_type
        Params:
            page_index: int
            page_size: int
            rec_type: String
            rec_status: STRING
        Returns:
            Array: filtered paginated results
        """
        logger.info("Processing all Recommendation")

        qry = cls.query
        filters = []
        if rec_type:
            filters.append(Recommendation.recommendation_type == rec_type)
        if rec_status:
            filters.append(Recommendation.status == rec_status)
        qry = qry.filter(db.and_(*filters))

        return qry.paginate(page=page_index, per_page=page_size, error_out=False)

    @classmethod
    def find(cls, recommendation_id: int):
        """Finds a Recommendation by it's ID"""
        logger.info("Processing lookup for id %s ...", recommendation_id)
        return cls.query.get(recommendation_id)

    @classmethod
    def find_or_404(cls, recommendation_id: int):
        """Find a Recommendation by it's id"""
        logger.info("Processing lookup or 404 for id %s ...", recommendation_id)
        return cls.query.get_or_404(recommendation_id)

    @classmethod
    def find_by_source_item_id(
        cls, source_item_id: int, sort_order: str = "desc"
    ) -> list:
        """Returns all Recommendations with the given source_item_id,
        sorted by recommendation_weight"""
        logger.info(
            """Processing source id query for %s
             sorting by rec weight in %s order...""",
            source_item_id,
            sort_order,
        )
        if sort_order == "asc":
            return (
                cls.query.filter(cls.source_item_id == source_item_id)
                .order_by(cls.recommendation_weight.asc())
                .all()
            )
        return (
            cls.query.filter(cls.source_item_id == source_item_id)
            .order_by(cls.recommendation_weight.desc())
            .all()
        )

    @classmethod
    def filter_all_by_status(cls, status):
        """Returns all of recommendations filtered by status in the database"""
        logger.info("Filtering and returning all recommendations by status")
        return cls.query.filter(cls.status == status)

    @classmethod
    def find_by_recommendation_type(
        cls, recommendation_type: RecommendationType = RecommendationType.UNKNOWN
    ) -> list:
        """Returns all Recommendations by their Type

        :param recommendation_type: values are
          ['UNKNOWN', 'UP_SELL', 'CROSS_SELL', 'ACCESSORY', 'COMPLEMENTARY', 'SUBSTITUTE']
        :type available: enum

        :return: a collection of Recommendations that are available
        :rtype: list

        """
        logger.info(
            "Processing recommendation type query for %s ...", recommendation_type.name
        )
        return cls.query.filter(cls.recommendation_type == recommendation_type)

    @classmethod
    def find_valid_by_source_item_id(
        cls, source_item_id: int, sort_order: str = "desc"
    ) -> list:
        """Returns all valid recommendations with the given
         source_item_id, sorted by recommendation_weight"""
        logger.info(
            """Processing valid recommendations query for source item id %s
            with sorting by recommendation weight in %s order.""",
            source_item_id,
            sort_order,
        )
        query = cls.query.filter(
            cls.source_item_id == source_item_id,
            cls.status == RecommendationStatus.VALID,
        )
        if sort_order == "asc":
            return query.order_by(cls.recommendation_weight.asc()).all()
        return query.order_by(cls.recommendation_weight.desc()).all()

    # @classmethod
    # def find_by_target_item_id(cls, target_item_id: int) -> list:
    #     """Returns all Recommendation with the given target_item_id"""
    #     logger.info("Processing target item id query for %s ...", target_item_id)
    #     return cls.query.filter(cls.target_item_id == target_item_id)

    # @classmethod
    # def find_by_recommendation_status(
    #     cls, recommendation_status: RecommendationStatus = RecommendationStatus.UNKNOWN
    # ) -> list:
    #     """Returns all Recommendations by their Status

    #     :param recommendation_status: values are
    #       ['UNKNOWN', 'VALID', 'OUT_OF_STOCK', 'DEPRECATED']

    #     :type available: enum

    #     :return: a collection of Recommendations that are available
    #     :rtype: list

    #     """
    #     logger.info(
    #         "Processing recommendation status query for %s ...",
    #         recommendation_status.value,
    #     )
    #     return cls.query.filter(cls.status == recommendation_status)


# find_top5_by_source_item_id

# find_top5_by_target_item_id

# find_by_source_item_name_fuzzy

# find_by_target_item_name_fuzzy

# find_top5_by_source_item_name_fuzzy

# find_top5_by_target_item_name_fuzzy

# find_item_created_after

# find_item_created_before

# find_item_updated_after

# find_item_updated_before
