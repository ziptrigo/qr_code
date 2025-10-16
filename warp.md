# QR Code Generator Project

## Project Overview
A Python project for generating and manipulating QR codes.

## Goals
- Create a flexible QR code generation service
- Support main QR code format
- Provide API, CLI and programmatic interfaces

## Tech Stack
- Python 3.13
- Django 5.2
- segno package for QR code generation
- RDBMS for data storage

## Current Status
Project setup phase - defining requirements and architecture.

## Next Steps
1. Research QR code libraries (qrcode, segno, etc.)
2. Define project structure
3. Implement basic QR code generation functionality
4. Create API interface
5. Create CLI interface

## Notes
### Functionality
1. Create QR code
When creating a QR code, the user should be able to specify the following:
- QR code format
- QR code content
- QR code size
- QR code error correction level
- QR code border
- QR code background color
- QR code foreground color
- QR code logo
- QR code logo size
- QR code data
- If the data is a url, then the user should be able to select whether the
  QR code will have that exact url, or a shortened url. The shortened url
  should be generated using functionality in this project that will point to
  an api endpoint that will then retrieve the original url from the DB.

2. API interface
The backend service is implemented in Django. The APIs are:
   2.1. Create QR code: A POST endpoint with the payload described above.
   2.2. Retrieve QR code: An endpoint that will save in the DB the number
        of times the QR code was read (ie, the endpoint was called) and
        forward the user to the original url.
