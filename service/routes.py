"""
My Service

Describe what your service does here
"""

from flask import jsonify, request, url_for, abort
from flask_restx import Resource, fields, reqparse, inputs
from service.common import status  # HTTP Status Codes
from service.models import Customer
from . import app, api


######################################################################
# GET INDEX
######################################################################


@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
# check service health
######################################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify({"status": "OK"}), status.HTTP_200_OK


# Define the model so that the docs reflect what can be sent
create_model = api.model(
    "Customer",
    {
        "first_name": fields.String(
            required=True, description="The first name of the Customer"
        ),
        "last_name": fields.String(
            required=True, description="The last name of the Customer"
        ),
        "address": fields.String(
            required=True,
            description="The address of the Customer",
        ),
        "active": fields.Boolean(
            required=True, description="Is the customer active or not"
        ),
    },
)

customer_model = api.inherit(
    "CustomerModel",
    create_model,
    {
        "id": fields.String(
            readOnly=True, description="The unique id assigned internally by service"
        ),
    },
)

# query string arguments
customer_args = reqparse.RequestParser()
customer_args.add_argument(
    "first_name",
    type=str,
    location="args",
    required=False,
    help="List Customers by first name",
)
customer_args.add_argument(
    "last_name",
    type=str,
    location="args",
    required=False,
    help="List Customers by last name",
)
customer_args.add_argument(
    "active",
    type=inputs.boolean,
    location="args",
    required=False,
    help="List Customers by active",
)

######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
#  PATH: /customers/{id}
######################################################################
class CustomerResource(Resource):
    """
    CustomerResource class

    Allows the manipulation of a single Customer
    GET /customer{id} - Returns a Customer with the id
    PUT /customer{id} - Update a Customer with the id
    DELETE /customer{id} -  Deletes a Customer with the id
    """

    # ------------------------------------------------------------------
    # READ A Customer
    # ------------------------------------------------------------------
    @api.doc("get_customers")
    @api.response(404, "Customer not found")
    @api.marshal_with(customer_model)
    def get(self, customer_id):
        """
        Retrieve a single Customer

        This endpoint will return a Customer based on it's id
        """
        app.logger.info("Request to Retrieve a customer with id [%s]", customer_id)
        customer = Customer.find(customer_id)
        if not customer or not customer.status:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        app.logger.info(
            "Returning customer: %s %s", customer.first_name, customer.last_name
        )
        return customer.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING Customer
    # ------------------------------------------------------------------
    @api.doc("update_customers")
    @api.response(404, "Customer not found")
    @api.response(400, "The posted Customer data was not valid")
    @api.expect(customer_model)
    @api.marshal_with(customer_model)
    def put(self, customer_id):
        """
        Update a Customer

        This endpoint will update a Customer based the body that is posted
        """
        app.logger.info("Request to update a customer with id [%s]", customer_id)
        customer = Customer.find(customer_id)
        if not customer or not customer.status:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        customer.deserialize(data)
        if not customer.status:
            abort(
                status.HTTP_400_BAD_REQUEST,
                "Cannot update the status.",
            )
        customer.id = customer_id
        customer.update()

        app.logger.info("Customer with ID [%s] updated.", customer.id)
        return customer.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A Customer
    # ------------------------------------------------------------------
    @api.doc("delete_customers")
    @api.response(204, "Customer deleted")
    def delete(self, customer_id):
        """
        Delete a Customer

        This endpoint will delete a Customer based the id specified in the path
        """
        app.logger.info("Request to Delete a customer with id [%s]", customer_id)
        customer = Customer.find(customer_id)
        if customer:
            customer.delete()
            app.logger.info("Customer with id [%s] was deleted", customer_id)

        return "", status.HTTP_204_NO_CONTENT

######################################################################
#  PATH: /customers
######################################################################
@api.route("/customers", strict_slashes=False)
class CustomerCollection(Resource):
    """Handles all interactions with collections of Customers"""

    # ------------------------------------------------------------------
    # LIST ALL EXISTING Customers
    # ------------------------------------------------------------------
    @api.doc("list_customers")
    @api.expect(customer_args, validate=True)
    @api.marshal_list_with(customer_model)
    def get(self):
        """Returns all of the Customers"""
        app.logger.info("Request for customer list")
        customers = []
        args = customer_args.parse_args()
        if args["first_name"] and args["last_name"]:
            app.logger.info("Filtering by name: %s %s", args["first_name"], args["last_name"])
            customers = Customer.find_by_name(args["first_name"], args["last_name"])
        elif args["first_name"]:
            app.logger.info("Filtering by first name: %s", args["first_name"])
            customers = Customer.find_by_first_name(args["first_name"])
        elif args["last_name"]:
            app.logger.info("Filtering by last name: %s", args["last_name"])
            customers = Customer.find_by_last_name(args["last_name"])
        elif args["address"]:
            app.logger.info("Filtering by address: %s", args["address"])
            customers = Customer.find_by_address(args["address"])
        else:
            app.logger.info("Returning unfiltered list.")
            customers = Customer.all()

        app.logger.info("[%s] Customers returned", len(customers))
        results = [customer.serialize() for customer in customers]
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW Customer
    # ------------------------------------------------------------------
    @api.doc("create_customers")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_model)
    @api.marshal_with(customer_model, code=201)
    def post(self):
        """
        Creates a Customer
        This endpoint will create a Customer based the data in the body that is posted
        """
        app.logger.info("Request to Create a Customer")
        customer = Customer()
        # app.logger.debug("Payload = %s", api.payload)
        customer.deserialize(api.payload)
        customer.create()
        app.logger.info("Customer with new id [%s] created!", customer.id)
        location_url = api.url_for(CustomerResource, customer_id=customer.id, _external=True)
        return customer.serialize(), status.HTTP_201_CREATED, {"Location": location_url}



######################################################################
#  PATH: /customers/{id}/deactivate
######################################################################
class DeactivateResource(Resource):
    """Handles deactivate endpoint"""

    @api.doc("deactivate_customers")
    @api.response(200, "Customer deactivated")
    @api.response(404, "Customer not found")
    def deactivate_customers(self, customer_id):
        """
        Deactivate a Customer

        This endpoint will deactivate a Customer based the id specified in the path
        """
        app.logger.info("Request to deactivate customer with id: %s", customer_id)
        customer = Customer.find(customer_id)
        if customer:
            customer.deactivate()
        else:
            abort(
                    status.HTTP_404_NOT_FOUND,
                    f"Customer with id '{customer_id}' was not found.",
                )

        app.logger.info("Customer with ID [%s] deactivate complete.", customer_id)
        return "", status.HTTP_200_OK


#####################################################################
#  PATH: /customers/{id}/deactivate
######################################################################
class RestoreResource(Resource):
    """Handles restore endpoint"""

    @api.doc("restore_customers")
    @api.response(200, "Customer restored")
    @api.response(404, "Customer not found")
    @api.marshal_with(customer_model)
    def restore_customers(self, customer_id):
        """
        Restore the account by its ID
        """
        app.logger.info("Request for restoring customer with id: %s", customer_id)
        customer = Customer.find(customer_id)
        if not customer:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        customer.status = True
        app.logger.info("Customer with ID [%s] restored.", customer.id)
        return customer.serialize(), status.HTTP_200_OK
