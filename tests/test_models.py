"""
Test cases for Customer Model

"""
import os
import logging
import unittest
from service.models import Customer, DataValidationError, db
from service import app
from tests.factories import CustomerFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  Customer   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestCustomer(unittest.TestCase):
    """Test Cases for Customer Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Customer.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Customer).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_object(self):
        """It should create a customer object"""
        customer = Customer(
            first_name="Michael",
            last_name="Parker",
            address="1724 Green Acres Road, Rocky Mount, New York, 00000",
        )
        self.assertEqual(str(customer), "<Customer Michael Parker id=[None]>")
        self.assertTrue(customer is not None)
        self.assertEqual(customer.id, None)
        self.assertEqual(customer.first_name, "Michael")
        self.assertEqual(customer.last_name, "Parker")
        self.assertEqual(
            customer.address, "1724 Green Acres Road, Rocky Mount, New York, 00000"
        )


#    def test_add_a_customer(self):
#        """It should Create a customer and add it to the database"""
#        customers = Customer.all()
#        self.assertEqual(customers, [])
#        customer = Customer(
#            first_name="Michael",
#            last_name="Parker",
#            address="1724 Green Acres Road, Rocky Mount, New York, 00000",
#        )
#        self.assertTrue(customer is not None)
#        self.assertEqual(customer.id, None)
#        customer.create()
#        # Assert that it was assigned an id and shows up in the database
#        self.assertIsNotNone(customer.id)
#        customers = Customer.all()
#        self.assertEqual(len(customers), 1)
