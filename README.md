# simple-blocking-eventlet

This app is meant to test/demonstrate a bug(?) seen when MS SQL Server is hit with many asynchronous requests. This project is meant to be a stripped down [MCRE](https://stackoverflow.com/help/minimal-reproducible-example) of [flask-app-simple-blocking-eventlet](https://github.com/bpaterni/flask-app-simple-blocking-eventlet)

## Installation

Some work has been done to hopefully make this demo app easy to use, but there is some setup involved. To run with different database backends, you'll need access to MSSQL and/or PostgreSQL databases. The respective docker containers are useful here:

* [PostgreSQL](https://hub.docker.com/_/postgres/)
* [MS SQL Server](https://docs.microsoft.com/en-us/sql/linux/quickstart-install-connect-docker?view=sql-server-2017)

Also, to connect to a SQL Server database, the ODBC client driver from Microsoft is required:

* [MSSQL ODBC Driver](https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-2017)

Install software dependencies:

    # pipenv sync

## Usage

Once database dependencies are acquired, you should be ready to execute the a simple demo:

    ## Start dockerized SQL Server
    $ ./start-mssql
    
    ## execute application
    $ pipenv run python app.py
