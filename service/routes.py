"""
My Service

Describe what your service does here
"""

from flask import jsonify, request, url_for, abort

# from flask import request

from service.common import status  # HTTP Status Codes

from service.models import Customer

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Customer Demo REST API Service",
            version="2.0",
            paths=url_for("list_customers", _external=True),
        ),
        # "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


# Place your REST API code here ...


######################################################################
# check service health
######################################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify({"status": 'OK'}), status.HTTP_200_OK


######################################################################
# ADD A NEW Customer
######################################################################
@app.route("/customers", methods=["POST"])
def create_customers():
    """
    Creates a Customer
    This endpoint will create a Customer based the data in the body that is posted
    """
    app.logger.info("Request to create a customer")
    # check_content_type("application/json")
    customer = Customer()
    customer.deserialize(request.get_json())
    customer.create()
    message = customer.serialize()
    location_url = url_for("create_customers", customer_id=customer.id, _external=True)

    app.logger.info("Customer with ID [%s] created.", customer.id)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# UPDATE AN EXISTING Customer
######################################################################
@app.route("/customers/<int:customer_id>", methods=["PUT"])
def update_customers(customer_id):
    """
    Update a Customer

    This endpoint will update a Customer based the body that is posted
    """
    app.logger.info("Request to update customer with id: %s", customer_id)
    # check_content_type("application/json")

    customer = Customer.find(customer_id)
    if not customer or not customer.status:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Customer with id '{customer_id}' was not found.",
        )

    customer.deserialize(request.get_json())
    if not customer.status:
        abort(
            status.HTTP_405_METHOD_NOT_ALLOWED,
            "Cannot update the status.",
        )
    customer.id = customer_id
    customer.update()

    app.logger.info("Customer with ID [%s] updated.", customer.id)
    return jsonify(customer.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A Customer
######################################################################


@app.route("/customers/<int:customer_id>", methods=["DELETE"])
def delete_customers(customer_id):
    """
    Delete a Customer

    This endpoint will delete a Customer based the id specified in the path
    """
    app.logger.info("Request to delete customer with id: %s", customer_id)
    customer = Customer.find(customer_id)
    if customer:
        customer.delete()

    app.logger.info("Customer with ID [%s] delete complete.", customer_id)
    return "", status.HTTP_204_NO_CONTENT


######################################################################
# READ A Customer
######################################################################


@app.route("/customers/<int:customer_id>", methods=["GET"])
def read_customers(customer_id):
    """
    Read a single Customer

    This endpoint will return a Customer based on it's id
    """
    app.logger.info("Request for customer with id: %s", customer_id)
    customer = Customer.find(customer_id)
    if not customer or not customer.status:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Customer with id '{customer_id}' was not found.",
        )

    app.logger.info(
        "Returning customer: %s %s", customer.first_name, customer.last_name
    )
    return jsonify(customer.serialize()), status.HTTP_200_OK


######################################################################
# List All EXISTING Customer
######################################################################


@app.route("/customers", methods=["GET"])
def list_customers():
    """
    Returns all of the customers
    """
    app.logger.info("Request for customer list")
    customers = []
    first_name = request.args.get("first_name")
    last_name = request.args.get("last_name")
    address = request.args.get("address")
    if first_name and last_name:
        # Find by name
        customers = Customer.find_by_name(first_name, last_name)
    elif first_name:
        customers = Customer.find_by_first_name(first_name)
    elif last_name:
        customers = Customer.find_by_last_name(last_name)
    elif address:
        customers = Customer.find_by_address(address)
    else:
        customers = Customer.all()
    # customers = Customer.all()

    results = [customer.serialize() for customer in customers if customer.status]
    app.logger.info("Returning %d customers", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# DEACTIVATE A Customer
######################################################################


@app.route("/customers/<int:customer_id>/deactivate", methods=["PUT"])
def deactivate_customers(customer_id):
    """
    Deactivate a Customer

    This endpoint will deactivate a Customer based the id specified in the path
    """
    app.logger.info("Request to deactivate customer with id: %s", customer_id)
    customer = Customer.find(customer_id)
    if customer:
        customer.deactivate()

    app.logger.info("Customer with ID [%s] deactivate complete.", customer_id)
    return "", status.HTTP_200_OK


######################################################################
# Restore a deactivated Customer account by its customerID
######################################################################


@app.route("/customers/<int:customer_id>/restore", methods=["PUT"])
def restore_customers(customer_id):
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
    return jsonify(customer.serialize()), status.HTTP_200_OK
