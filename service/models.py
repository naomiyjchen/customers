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

    def create(self):
        """
        Creates a Customer to the database
        """
        logger.info("Creating %s %s", self.first_name, self.last_name)
        # id must be none to generate next primary key
        self.id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Customer to the database
        """
        logger.info("Saving %s %s", self.first_name, self.last_name)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """Removes a Customer from the data store"""
        logger.info("Deleting %s %s", self.first_name, self.last_name)
        db.session.delete(self)
        db.session.commit()

    def list(self):
        """
        List all the customers in the database
        """
        logger.info("Listing %s %s", self.first_name, self.last_name)

        db.session.list(self)
        db.session.commit()

    def serialize(self) -> dict:
        """Serializes a Customer into a dictionary"""
        return {
            "id": self.id,
            "first name": self.first_name,
            "last name": self.last_name,
            "address": self.address,
        }

    def deserialize(self, data: dict):
        """
        Deserializes a Customer from a dictionary
        Args:
            data (dict): A dictionary containing the Customer data
        """
        try:
            self.first_name = data["first name"]
            self.last_name = data["last name"]
            self.address = data["address"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid pet: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid pet: body of request contained bad or no data " + str(error)
            ) from error
        return self

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

    @classmethod
    def all(cls):
        """Returns all of the Customers in the database"""
        logger.info("Processing all Customers")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Customer by its ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_first_name(cls, first_name: str) -> list:
        """Returns all Customers with the first name

        :param first_name: the first name of the Customers you want to match
        :type first_name: str

        :return: a collection of Customers with that first name
        :rtype: list

        """
        logger.info("Processing first name query for %s ...", first_name)
        return cls.query.filter(cls.first_name == first_name)

    @classmethod
    def find_by_last_name(cls, last_name: str) -> list:
        """Returns all of the Customers with last name

        :param last_name: the last name of the Customers you want to match
        :type last_name: str

        :return: a collection of Customers with that last name
        :rtype: list

        """
        logger.info("Processing last name query for %s ...", last_name)
        return cls.query.filter(cls.last_name == last_name)

    # @classmethod
    # def find_by_address(cls, address:str) -> list:


#    @classmethod
#    def find_by_name(cls, name):
#        """Returns all Customers with the given name
#
#        Args:
#            name (string): the name of the Customers you want to match
#        """
#        logger.info("Processing name query for %s ...", name)
#        return cls.query.filter(cls.name == name)
