# TechConf Registration Website

## Project Overview
The TechConf website allows attendees to register for an upcoming conference. Administrators can also view the list of attendees and notify all attendees via a personalized email message.

The application is currently working but the following pain points have triggered the need for migration to Azure:
 - The web application is not scalable to handle user load at peak
 - When the admin sends out notifications, it's currently taking a long time because it's looping through all attendees, resulting in some HTTP timeout exceptions
 - The current architecture is not cost-effective 

In this project, you are tasked to do the following:
- Migrate and deploy the pre-existing web app to an Azure App Service
- Migrate a PostgreSQL database backup to an Azure Postgres database instance
- Refactor the notification logic to an Azure Function via a service bus queue message

## Dependencies

You will need to install the following locally:
- [Postgres](https://www.postgresql.org/download/)
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Azure Function tools V3](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#install-the-azure-functions-core-tools)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [Azure Tools for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)

## Project Instructions

### Part 1: Create Azure Resources and Deploy Web App
1. Create a Resource group
2. Create an Azure Postgres Database single server
   - Add a new database `techconfdb`
   - Allow all IPs to connect to database server
   - Restore the database with the backup located in the data folder
3. Create a Service Bus resource with a `notificationqueue` that will be used to communicate between the web and the function
   - Open the web folder and update the following in the `config.py` file
      - `POSTGRES_URL`
      - `POSTGRES_USER`
      - `POSTGRES_PW`
      - `POSTGRES_DB`
      - `SERVICE_BUS_CONNECTION_STRING`
4. Create App Service plan
5. Create a storage account
6. Deploy the web app

### Part 2: Create and Publish Azure Function
1. Create an Azure Function in the `function` folder that is triggered by the service bus queue created in Part 1.

      **Note**: Skeleton code has been provided in the **README** file located in the `function` folder. You will need to copy/paste this code into the `__init.py__` file in the `function` folder.
      - The Azure Function should do the following:
         - Process the message which is the `notification_id`
         - Query the database using `psycopg2` library for the given notification to retrieve the subject and message
         - Query the database to retrieve a list of attendees (**email** and **first name**)
         - Loop through each attendee and send a personalized subject message
         - After the notification, update the notification status with the total number of attendees notified
2. Publish the Azure Function

### Part 3: Refactor `routes.py`
1. Refactor the post logic in `web/app/routes.py -> notification()` using servicebus `queue_client`:
   - The notification method on POST should save the notification object and queue the notification id for the function to pick it up
2. Re-deploy the web app to publish changes

## Monthly Cost Analysis
Complete a month cost analysis of each Azure resource to give an estimate total cost using the table below:
As per [Azure Resource Pricing Calculator](https://azure.microsoft.com/en-in/pricing/calculator/) -

| Azure Resource | Service Tier | Monthly Cost (USD) |
| ------------ | ------------ | ------------ |
| *Azure Postgres Database* |  Compute = 27.86 x vCores (1), Storage = 0.11 x Storage Units (5)   |       ~28       |
| *Azure Service Bus*   |     Basic    |        0.05 per million operations      |
| *Azure Function*                   |   3M executions and 1.5 million GB/s (first 400,000 GB/s of execution and 1,000,000 executions are free)      |      18        |
| *App Service*      | Free Tier | 0  |
| *App Service*| Standard | 73|
| *Azure Storage* | 100 TB Storage + 1M writes + 1M list + 1M read | ~2049 |

## Architecture Explanation
#### Azure Function
* Azure Functions allows to run small pieces of code (called "functions") without worrying about application infrastructure (serverless) and thus makes the app development process more productive.
* Pay only for the time spent running your code.
* It is mostly suitable for running background jobs or respond to events like sending notification on user registration etc. This helps to avoid blocking the code execution and hence timeouts in the web app.

####  Azure Web App 
One of the major concerns of the on-premise solutions is they need dedicated on-site servers, which are still costly and often require more than a one-time purchase. Keeping your data accessible and secure requires hardware that is not only up to date to handle all relevant requests but also compatible with other server systems and updated software systems. So there is a recurring cost every time you need to update your hardware. They also requires a dedicated tech team to support all of the updates needed to keep these servers functional.
On the other hand cloud services are cheaper than on-premise solutions. With Azure, you don’t have to invest in new machines, infrastructure, or replace aging servers. You also don’t need to make space for infrastructure and servers. Azure, offers flexible expenditure, which means:
- You pay according to your needs.
- You pay more to get more.
- You save on energy, space, and cooling costs.
Not only that, you have certainty in your recurring costs as Microsoft charge per user for their Azure cloud services.