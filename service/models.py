"""
Models for Customer

All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


# Function to initialize the database
def init_db(app):
    """Initializes the SQLAlchemy app"""
    Customer.init_db(app)


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Customer(db.Model):
    """
    Class that represents a Customer
    """

    app = None

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(63), nullable=False)
    last_name = db.Column(db.String(63), nullable=False)
    address = db.Column(db.String(200), nullable=False)

    ##################################################
    # Instance Methods
    ##################################################
    def __repr__(self):
        """Used for debugging"""
        return f"<Customer {self.first_name} {self.last_name} id=[{self.id}]>"

    ##################################################
    # Class Methods
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


#    @classmethod
#    def all(cls):
#        """Returns all of the Customers in the database"""
#        logger.info("Processing all Customers")
#        return cls.query.all()


#    @classmethod
#    def find(cls, by_id):
#        """Finds a Customer by it's ID"""
#        logger.info("Processing lookup for id %s ...", by_id)
#        return cls.query.get(by_id)


#    @classmethod
#    def find_by_name(cls, name):
#        """Returns all Customers with the given name
#
#        Args:
#            name (string): the name of the Customers you want to match
#        """
#        logger.info("Processing name query for %s ...", name)
#        return cls.query.filter(cls.name == name)
