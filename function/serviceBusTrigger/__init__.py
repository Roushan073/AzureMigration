import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):

    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s', notification_id)

    # TODO: Get connection to database
    connection = psycopg2.connect(user="postgres@azure-pg-server",
                                  password="",
                                  host="azure-pg-server.postgres.database.azure.com",
                                  port="5432",
                                  database="techconfdb")

    # Log PostgreSQL Connection properties
    logging.info("Connection Properties: {}".format(connection.get_dsn_parameters()))

    cursor = connection.cursor()

    try:
        # TODO: Get notification message and subject from database using the notification_id
        notification_query = "select message, subject from notification where id = {};".format(notification_id)
        logging.info('Executing Query: {}'.format(notification_query))
        cursor.execute(notification_query)
        notification_records = cursor.fetchall()
        message, subject = notification_records[0][0], notification_records[0][1]
        logging.info("Notification Message: {}, Subject: {}".format(message, subject))

        # TODO: Get attendees email and name
        attendees_query = "select first_name, last_name, email from attendee;"
        logging.info('Executing Query: {}'.format(attendees_query))
        cursor.execute(attendees_query)
        attendees = cursor.fetchall()
        logging.info("Total Attendees: {}".format(len(attendees)))

        for attendee in attendees:
            subject = '{}: {}'.format(attendee[0], subject)
            send_email(attendee[2], subject, message)

        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        notification_completed_date = datetime.utcnow()
        notification_status = 'Notified {} attendees'.format(len(attendees))

        notification_update_query = "update notification set status = '{}', completed_date = '{}' where id = {};".format(
            notification_status, notification_completed_date, notification_id
        )
        logging.info('Executing Query: {}'.format(notification_update_query))
        cursor.execute(notification_update_query)
        connection.commit()
        logging.info('Notification updated successfully.')

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error('Exception while executing query: {}'.format(error))
    finally:
        # TODO: Close connection
        if connection:
            cursor.close()
            connection.close()
            logging.info("PostgreSQL connection closed successfully.")


def send_email(email, subject, body):
    logging.info('Sending Notification: {} to: {}'.format(body, email))
    ADMIN_EMAIL_ADDRESS = 'info@techconf.com'
    SENDGRID_API_KEY = '' #Configuration not required, required SendGrid Account

    if not app.config.get('SENDGRID_API_KEY'):
        message = Mail(
            from_email=ADMIN_EMAIL_ADDRESS,
            to_emails=email,
            subject=subject,
            plain_text_content=body)

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)