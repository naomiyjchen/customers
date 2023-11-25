Feature: The customer service back-end
    As a Service Provider
    I need a RESTful customer data service
    So that I can keep track of all my customers

Background:
    Given the following customers
        | first_name | last_name | address                                             | active |
        | Michael    | Parker    | 1724 Green Acres Road, Rocky Mount, New York, 00000 | true   |
        | Keith      | Rasmussen | 7776 King Points New Melanieland, TX, 22788         | true   |
        
Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Customer RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Customer
    When I visit the "Home Page"
    And I set the "First Name" to "Tom"
    And I set the "Last Name" to "Cruise"
    And I select "True" in the "Status" dropdown
    And I set the "Address" to "123 fake street, fake city, fake state"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "ID" field
    And I press the "Clear" button
    Then the "ID" field should be empty
    And the "First Name" field should be empty
    And the "Last Name" field should be empty
    And the "Address" field should be empty
    When I paste the "ID" field
    And I press the "Read" button
    Then I should see the message "Success"
    And I should see "Tom" in the "First Name" field
    And I should see "Cruise" in the "Last Name" field
    And I should see "True" in the "Status" dropdown
    And I should see "123 fake street, fake city, fake state" in the "Address" field

Scenario: Query by first name 
    When I visit the "Home Page"
    And I set the "First Name" to "Michael"
    And I press the "Query" button
    Then I should see the message "Success"
    And I should see "Michael" in the results

Scenario: Query by Name
    When I visit the "Home Page"
    And I set the "First Name" to "Michael"
    And I set the "Last Name" to "Parker"
    And I press the "Query" button
    Then I should see the message "Success"
    And I should see "Michael" in the results

Scenario: Query by last name 
    When I visit the "Home Page"
    And I set the "Last Name" to "Parker"
    And I press the "Query" button
    Then I should see the message "Success"
    And I should see "Michael" in the results

Scenario: Query by address
    When I visit the "Home Page"
    And I set the "Address" to "1724 Green Acres Road, Rocky Mount, New York, 00000"
    And I press the "Query" button
    Then I should see the message "Success"
    And I should see "Michael" in the results


Scenario: Update a Customer
    When I visit the "Home Page"
    And I set the "First Name" to "Michael"
    And I press the "Query" button
    Then I should see the message "Success"
    And I should see "Michael" in the "First Name" field
    And I should see "Parker" in the "Last Name" field
    And I should see "1724 Green Acres Road, Rocky Mount, New York, 00000" in the "Address" field
    When I change "First Name" to "Mike"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "ID" field
    And I press the "Clear" button
    And I paste the "ID" field
    And I press the "Read" button
    Then I should see the message "Success"
    And I should see "Mike" in the "First Name" field
    When I press the "Clear" button
    And I press the "Query" button
    Then I should see the message "Success"
    And I should see "Mike" in the results
    And I should not see "Michael" in the results
