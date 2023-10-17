# NYU DevOps Project Template

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

This is a skeleton you can use to start your projects

## Overview

This project is about a representation of the customer accounts of the E-Commerce website for NYU CSCI-GA 2820, Fall 2023.

## Automatic Setup

The best way to use this repo is to start your own repo using it as a git template. To do this just press the green **Use this template** button in GitHub and this will become the source for your repository.

## Manual Setup

You can also clone this repository and then copy and paste the starter code into your project repo folder on your local computer. Be careful not to copy over your own `README.md` file so be selective in what you copy.

There are 4 hidden files that you will need to copy manually if you use the Mac Finder or Windows Explorer to copy files from this folder into your repo folder.

These should be copied using a bash shell as follows:

```bash
    cp .gitignore  ../<your_repo_folder>/
    cp .flaskenv ../<your_repo_folder>/
    cp .gitattributes ../<your_repo_folder>/
```

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
requirements.txt    - list if Python libraries required by your code
config.py           - configuration parameters

service/                   - service python package
├── __init__.py            - package initializer
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/              - test cases package
├── __init__.py     - package initializer
├── test_models.py  - test suite for business models
└── test_routes.py  - test suite for service routes
```

## URLs
| HTTP Methods | URL | Description |
| ------- | ------- | ------- | 
| POST | "/customers" | Create a Customer Object | 
| GET | "/customers/<int:customer_id>" | List the information of the Customer with customer_id | 
| PUT | "/customers/<int:customer_id>" | Update the the information of Customer with the customer_id  | 
| DELETE | "/customers/<int:customer_id>" | Delete the Customer with customer_id | 

## API Calls

1. Create a customer record

   - Description
  
   - Request URL
  
   - Request Body
  
   - Response
  
   - Example

2. Update a customer record based on Customer ID

   - Description
  
   - Request URL
  
   - Request Body
  
   - Response
  
   - Example

3. Read a cutomer record based on Customer ID

   - Description
  
   - Request URL
  
   - Request Body
  
   - Response
  
   - Example

4. Delete a cutomer record based on Customer ID

   - Description
  
   - Request URL
  
   - Request Body
  
   - Response
  
   - Example

5. List all customer information

   - Description
  
   - Request URL
  
   - Request Body
  
   - Response
  
   - Example


## How to test

To test the code from the VScode terminal, run:

`green -vvv --processes=1 --run-coverage --termcolor --minimum-coverage=95`

## How to run

To start the service from the VScode terminal, run:

`honcho start`

## License

Copyright (c) John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by *John Rofrano*, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.

