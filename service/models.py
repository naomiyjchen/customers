"""
Models for Customer

All of the models are stored in this module
"""
import os
import json
import logging
from flask_sqlalchemy import SQLAlchemy
from retry import retry
from cloudant.client import Cloudant
from cloudant.query import Query
from cloudant.adapters import Replay429Adapter
from cloudant.database import CloudantDatabase
from requests import HTTPError, ConnectionError

# logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
# db = SQLAlchemy()
ADMIN_PARTY = os.environ.get("ADMIN_PARTY", "False").lower() == "true"
CLOUDANT_HOST = os.environ.get("CLOUDANT_HOST", "localhost")
CLOUDANT_USERNAME = os.environ.get("CLOUDANT_USERNAME", "admin")
CLOUDANT_PASSWORD = os.environ.get("CLOUDANT_PASSWORD", "pass")

# global variables for retry (must be int)
RETRY_COUNT = int(os.environ.get("RETRY_COUNT", 10))
RETRY_DELAY = int(os.environ.get("RETRY_DELAY", 1))
RETRY_BACKOFF = int(os.environ.get("RETRY_BACKOFF", 2))

# Function to initialize the database
# def init_db(app):
#     """Initializes the SQLAlchemy app"""
#     Customer.init_db(app)


class DatabaseConnectionError(Exception):
    """Custom Exception when database connection fails"""


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Customer:
    """
    Class that represents a Customer
    """

    logger = logging.getLogger(__name__)
    client: Cloudant = None
    database: CloudantDatabase = None

    def __init__(
        self,
        first_name: str = None,
        last_name: str = None,
        address: str = None,
        status: bool = True,
    ):
        """Constructor"""
        self.id = None
        self.last_name = last_name
        self.first_name = first_name
        self.address = address
        self.status = status

    def __repr__(self):
        """Used for debugging"""
        return f"<Customer {self.first_name} {self.last_name} id=[{self.id}]>"

    @retry(
        HTTPError,
        delay=RETRY_DELAY,
        backoff=RETRY_BACKOFF,
        tries=RETRY_COUNT,
        logger=logger,
    )
    def create(self):
        """
        Creates a Customer to the database
        """
        if (
            self.first_name is None or self.last_name is None
        ):  # name is the only required field
            raise DataValidationError("name attribute is not set")

        try:
            document = self.database.create_document(self.serialize())
        except HTTPError as err:
            Customer.logger.warning("Create failed: %s", err)
            return

        if document.exists():
            self.id = document["_id"]

    @retry(
        HTTPError,
        delay=RETRY_DELAY,
        backoff=RETRY_BACKOFF,
        tries=RETRY_COUNT,
        logger=logger,
    )
    def update(self):
        """
        Updates a Customer to the database
        """
        try:
            document = self.database[self.id]  # pylint: disable=unsubscriptable-object)
        except KeyError:
            document = None
        if document:
            document.update(self.serialize())
            document.save()

    @retry(
        HTTPError,
        delay=RETRY_DELAY,
        backoff=RETRY_BACKOFF,
        tries=RETRY_COUNT,
        logger=logger,
    )
    def delete(self):
        """Removes a Customer from the data store"""
        try:
            document = self.database[self.id]  # pylint: disable=unsubscriptable-object)
        except KeyError:
            document = None
        if document:
            document.delete()

    def serialize(self) -> dict:
        """Serializes a Customer into a dictionary"""
        customer = {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "address": self.address,
            "active": self.status,
        }
        if self.id:
            customer["_id"] = self.id
        return customer

    def deserialize(self, data: dict):
        """
        Deserializes a Customer from a dictionary
        Args:
            data (dict): A dictionary containing the Customer data
        """
        Customer.logger.info("deserialize(%s)", data)
        try:
            self.first_name = data["first_name"]
            self.last_name = data["last_name"]
            self.address = data["address"]
            if isinstance(data["active"], bool):
                self.status = data["active"]
            else:
                raise DataValidationError(
                    "Invalid type for boolean [active]: " + str(type(data["active"]))
                )
        except KeyError as error:
            raise DataValidationError(
                "Invalid customer: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid customer: body of request contained bad or no data "
                + str(error)
            ) from error
        if not self.id and "_id" in data:
            self.id = data["_id"]

        return self

    def deactivate(self):
        """set the status to false to deactivate account"""

        self.status = False

    ######################################################################
    #  S T A T I C   D A T A B S E   M E T H O D S
    ######################################################################
    @classmethod
    def connect(cls):
        """Connect to the server"""
        cls.client.connect()

    @classmethod
    def disconnect(cls):
        """Disconnect from the server"""
        cls.client.disconnect()

    @classmethod
    @retry(
        HTTPError,
        delay=RETRY_DELAY,
        backoff=RETRY_BACKOFF,
        tries=RETRY_COUNT,
        logger=logger,
    )
    def create_query_index(cls, field_name: str, order: str = "asc"):
        """Creates a new query index for searching"""
        cls.database.create_query_index(
            index_name=field_name, fields=[{field_name: order}]
        )

    @classmethod
    @retry(
        HTTPError,
        delay=RETRY_DELAY,
        backoff=RETRY_BACKOFF,
        tries=RETRY_COUNT,
        logger=logger,
    )
    def remove_all(cls):
        """Removes all documents from the database (use for testing)"""
        for document in cls.database:  # pylint: disable=(not-an-iterable
            document.delete()

    @classmethod
    @retry(
        HTTPError,
        delay=RETRY_DELAY,
        backoff=RETRY_BACKOFF,
        tries=RETRY_COUNT,
        logger=logger,
    )
    def all(cls):
        """Query that returns all Customers"""
        results = []
        for doc in cls.database:  # pylint: disable=not-an-iterable
            customer = Customer().deserialize(doc)
            customer.id = doc["_id"]
            results.append(customer)
        return results

    ######################################################################
    #  F I N D E R   M E T H O D S
    ######################################################################
    @classmethod
    @retry(
        HTTPError,
        delay=RETRY_DELAY,
        backoff=RETRY_BACKOFF,
        tries=RETRY_COUNT,
        logger=logger,
    )
    def find_by(cls, **kwargs):
        """Find records using selector"""
        query = Query(cls.database, selector=kwargs)
        results = []
        for doc in query.result:
            customer = Customer()
            customer.deserialize(doc)
            results.append(customer)
        return results

    @classmethod
    @retry(
        HTTPError,
        delay=RETRY_DELAY,
        backoff=RETRY_BACKOFF,
        tries=RETRY_COUNT,
        logger=logger,
    )
    def find(cls, customer_id: str):
        """Finds a Customer by its ID"""
        try:
            document = cls.database.get_document(
                customer_id
            )  # pylint: disable=unsubscriptable-object
            # Cloudant doesn't delete documents. :( It leaves the _id with no data
            # so we must validate that _id that came back has a valid _rev
            # if this next line throws a KeyError the document was deleted
            _ = document["_rev"]
            return Customer().deserialize(document)
        except KeyError:
            return None

    @classmethod
    # @retry(
    #     HTTPError,
    #     delay=RETRY_DELAY,
    #     backoff=RETRY_BACKOFF,
    #     tries=RETRY_COUNT,
    #     logger=logger,
    # )
    def find_by_first_name(cls, first_name: str):
        """Returns all Customers with the first name"""

        return cls.find_by(first_name=first_name)

    @classmethod
    # @retry(
    #     HTTPError,
    #     delay=RETRY_DELAY,
    #     backoff=RETRY_BACKOFF,
    #     tries=RETRY_COUNT,
    #     logger=logger,
    # )
    def find_by_last_name(cls, last_name: str):
        """Returns all of the Customers with last name"""
        return cls.find_by(last_name=last_name)

    @classmethod
    # @retry(
    #     HTTPError,
    #     delay=RETRY_DELAY,
    #     backoff=RETRY_BACKOFF,
    #     tries=RETRY_COUNT,
    #     logger=logger,
    # )
    # def find_by_name(cls, first_name: str, last_name: str) -> list:
    #     """Returns all Customers with the given name

    #     Args:
    #         name (string): the name of the Customers you want to match
    #     """
    #     logger.info("Processing name query for %s %s ...", first_name, last_name)
    #     return cls.query.filter(
    #         cls.first_name == first_name, cls.last_name == last_name
    #     )

    @classmethod
    # @retry(
    #     HTTPError,
    #     delay=RETRY_DELAY,
    #     backoff=RETRY_BACKOFF,
    #     tries=RETRY_COUNT,
    #     logger=logger,
    # )
    def find_by_address(cls, address: str):
        """Returns all Customers with the given address

        Args:
            address (string): the address of the Customers
        """

        return cls.find_by(address=address)

    ############################################################
    #  C L O U D A N T   D A T A B A S E   C O N N E C T I O N
    ############################################################

    @staticmethod
    def __check_for_cloud_foundry_binding():
        """Checks for Cloud Foundry environment"""
        opts = {}
        if "VCAP_SERVICES" in os.environ:
            Customer.logger.info("Found Cloud Foundry VCAP_SERVICES bindings")
            vcap_services = json.loads(os.environ["VCAP_SERVICES"])
            # Look for Cloudant in VCAP_SERVICES
            for service in vcap_services:
                if service.startswith("cloudantNoSQLDB"):
                    opts = vcap_services[service][0]["credentials"]
        return opts

    @staticmethod
    def __check_for_kubernetes_binding():
        """Checks for Kubernetes environment"""
        opts = {}
        if "BINDING_CLOUDANT" in os.environ:
            Customer.logger.info("Found Kubernetes BINDING_CLOUDANT bindings")
            opts = json.loads(os.environ["BINDING_CLOUDANT"])
        return opts

    @staticmethod
    def __check_for_local_binding():
        """Checks for local environment"""
        Customer.logger.info("Looking for local environment bindings")
        opts = {
            "username": CLOUDANT_USERNAME,
            "password": CLOUDANT_PASSWORD,
            "host": CLOUDANT_HOST,
            "port": 5984,
            "url": "http://" + CLOUDANT_HOST + ":5984/",
        }
        return opts

    @staticmethod
    def init_db(dbname: str = "customers"):
        """
        Initialized Cloudant database connection
        """
        # See if we are running Cloud Foundry
        opts = Customer.__check_for_cloud_foundry_binding()

        # if VCAP_SERVICES isn't found, maybe we are running on Kubernetes?
        if not opts:
            opts = Customer.__check_for_kubernetes_binding()

        # If Cloudant not found in VCAP_SERVICES or BINDING_CLOUDANT
        # get it from the CLOUDANT_xxx environment variables
        if not opts:
            opts = Customer.__check_for_local_binding()

        if any(k not in opts for k in ("host", "username", "password", "port", "url")):
            raise DatabaseConnectionError(
                "Error - Failed to retrieve options. "
                "Check that app is bound to a Cloudant service."
            )

        Customer.logger.info("Cloudant Endpoint: %s", opts["url"])
        try:
            if ADMIN_PARTY:
                Customer.logger.info("Running in Admin Party Mode...")
            Customer.client = Cloudant(
                opts["username"],
                opts["password"],
                url=opts["url"],
                connect=True,
                auto_renew=True,
                admin_party=ADMIN_PARTY,
                adapter=Replay429Adapter(retries=10, initialBackoff=0.01),
            )

        except ConnectionError as exc:
            raise DatabaseConnectionError(
                "Cloudant service could not be reached"
            ) from exc

        # Create database if it doesn't exist
        try:
            Customer.database = Customer.client.get_database(dbname)
            # pylint: disable=unsubscriptable-object
        except KeyError:
            # Create a database using an initialized client
            Customer.database = Customer.client.create_database(dbname)
        # check for success
        if not Customer.database.exists():
            raise DatabaseConnectionError(f"Database [{dbname}] could not be obtained")


#    @classmethod
#     def init_db(cls, app):
#         """Initializes the database session"""
#         logger.info("Initializing database")
#         cls.app = app
#         # This is where we initialize SQLAlchemy from the Flask app
#         db.init_app(app)
#         app.app_context().push()
#         db.create_all()  # make our sqlalchemy tables
