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
    "" "Enumeration of recommendation status " ""
    UNKNOWN = 0
    VALID = 1
    OUT_OF_STOCK = 2
    DEPRECATED = 3


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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    ##################################################
    # INSTANCE METHODS
    ##################################################

    def __repr__(self):
        return f"<Recommendation {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Recommendation to the database
        """
        try:
            logger.info("Attempting to create Recommendation with ID %s", self.id)
            # id must be none to generate next primary key
            self.id = None  # pylint: disable=invalid-name
            db.session.add(self)
            db.session.commit()
            logger.info("Successfully created Recommendation with ID %s", self.id)
        except Exception as e:
            logger.error("Error creating Recommendation: %s", e)
            db.session.rollback()
            raise DataValidationError("Error creating Recommendation: " + str(e)) from e

    def update(self):
        """
        Updates a Recommendation to the database
        """
        logger.info("Saving %s", self.name)
        db.session.commit()

    def delete(self):
        """Removes a Recommendation from the data store"""
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """Serializes a Recommendation into a dictionary"""
        return {
            "id": self.id,
            "source_item_id": self.source_item_id,
            "target_item_id": self.target_item_id,
            "recommendation_type": self.recommendation_type.name,
            "recommendation_weight": self.recommendation_weight,
            "status": self.status.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def deserialize(self, data):
        """
        Deserializes a Recommendation from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.source_item_id = data["source_item_id"]
            self.target_item_id = data["target_item_id"]
            if "recommendation_type" in data:
                self.recommendation_type = RecommendationType[
                    data["recommendation_type"].upper()
                ]
            self.recommendation_weight = data["recommendation_weight"]
            if "status" in data:
                self.status = RecommendationStatus[data["status"].upper()]
            if "created_at" in data:
                self.created_at = datetime.fromisoformat(data["created_at"])
            if "updated_at" in data:
                self.updated_at = datetime.fromisoformat(data["updated_at"])
        except KeyError as error:
            raise DataValidationError(
                "Invalid Recommendation Type or Status : missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Recommendation: body of request contained bad or no data - "
                "Error message: " + error
            ) from error
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
    def find(cls, id: int):
        """Finds a Recommendation by it's ID"""
        logger.info("Processing lookup for id %s ...", id)
        return cls.query.get(id)

    @classmethod
    def find_or_404(cls, id: int):
        """Find a Recommendation by it's id"""

        logger.info("Processing lookup or 404 for id %s ...", id)
        return cls.query.get_or_404(id)

    @classmethod
    def find_by_source_item_id(cls, source_item_id: int) -> list:
        """Returns all Recommendation with the given source_item_id"""
        logger.info("Processing source_id query for %s ...", source_item_id)
        return cls.query.filter(cls.source_item_id == source_item_id)

    @classmethod
    def find_by_target_item_id(cls, target_item_id: int) -> list:
        """Returns all Recommendation with the given target_item_id"""
        logger.info("Processing source_id query for %s ...", target_item_id)
        return cls.query.filter(cls.target_item_id == target_item_id)

    @classmethod
    def find_by_recommendation_type(
        cls, recommendation_type: RecommendationType = RecommendationType.UNKNOWN
    ) -> list:
        """Returns all Recommendations by their Type

        :param recommendation_type: values are ['UNKNOWN', 'UP_SELL', 'CROSS_SELL', 'ACCESSORY', 'COMPLEMENTARY', 'SUBSTITUTE']
        :type available: enum

        :return: a collection of Recommendations that are available
        :rtype: list

        """
        logger.info("Processing gender query for %s ...", recommendation_type.name)
        return cls.query.filter(cls.recommendation_type == recommendation_type)

    @classmethod
    def find_by_recommendation_status(
        cls, recommendation_status: RecommendationStatus = RecommendationStatus.UNKNOWN
    ) -> list:
        """Returns all Recommendations by their Status

        :param recommendation_type: values are ['UNKNOWN', 'VALID', 'OUT_OF_STOCK', 'DEPRECATED']

        :type available: enum

        :return: a collection of Recommendations that are available
        :rtype: list

        """
        logger.info("Processing gender query for %s ...", recommendation_status.value)
        return cls.query.filter(cls.status == recommendation_status)


# TODO

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
