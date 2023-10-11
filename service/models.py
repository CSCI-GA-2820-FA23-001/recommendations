"""
Models for Recommendation

All of the models are stored in this module
"""
import datetime
import logging
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


# Function to initialize the database
def init_db(app):
    """ Initializes the SQLAlchemy app """
    Recommendation.init_db(app)


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """


class RecommendationType(Enum):
    """ Enumeration of recommendation type """
    UP_SELL = 1
    CROSS_SELL = 2
    ACCESSORY = 3


class RecommendationStatus(Enum):
    "" "Enumeration of recommendation status """
    VALID = "valid"
    OUT_OF_STOCK = "out of stock"
    DEPRECATED = "deprecated"


class Recommendation(db.Model):
    """
    Class that represents a Recommendation
    """

    app = None
    __tablename__ = "recommendation"

    # Table Schema
    recommendation_id = db.Column(db.Integer, primary_key=True)
    source_item_id = db.Column(db.Integer, nullable=False)
    target_item_id = db.Column(db.Integer, nullable=False)
    recommendation_type = db.Column(
        db.Enum(RecommendationType), server_default=(RecommendationType.UP_SELL.name)
    )
    recommendation_weight = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(
        db.Enum(RecommendationStatus), nullable=False, server_default=RecommendationStatus.VALID.value
    )
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<Recommendation {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Recommendation to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Recommendation to the database
        """
        logger.info("Saving %s", self.name)
        db.session.commit()

    def delete(self):
        """ Removes a Recommendation from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Recommendation into a dictionary """
        return {
            "id": self.recommendation_id,
            "source_item_id": self.source_item_id,
            "target_item_id": self.target_item_id,
            "recommendation_type": self.recommendation_type.name,
            "recommendation_weight": self.recommendation_weight,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at
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
            self.recommendation_type = RecommendationType[data["recommendation_type"].upper()]
            self.recommendation_weight = data["recommendation_weight"]
            self.status = RecommendationStatus[data["status"].replace("-", "_").upper()]
            if "created_at" in data:
                self.created_at = data["created_at"]
            if "updated_at" in data:
                self.updated_at = data["updated_at"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid Recommendation: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Recommendation: body of request contained bad or no data - "
                "Error message: " + error
            ) from error
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Recommendation in the database """
        logger.info("Processing all Recommendation")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a Recommendation by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Recommendation with the given name

        Args:
            name (string): the name of the Recommendation you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
