from flask import Flask, flash, request, render_template, redirect, url_for
import csv
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
# add sec variable
app.secret_key = 'c169f75250783502531a0aac1f89a1fd'
SMTP_SERVER = 'smtp.gmail.com'  # Use your SMTP server
SMTP_PORT = 587  # TLS # 465 SSL  # Use the appropriate port
# email to send the message from
# add sec variable
SMTP_USER = 'st.katherine.alexandria@gmail.com'
# password for email address
# add sec variable
SMTP_PASSWORD = 'lssz bwzn aayj rigz'
# add sec variable
SEND_PASSWORD = 'StKatherine'


@app.route('/', methods=['GET', 'POST'])
# Signup route to display the form to collect phone numbers and carriers
def index():
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        carrier = request.form['carrier']

        if is_registered(phone_number, carrier):
            flash("This phone number is already registered.", "text-red-500")
        elif update_carrier(phone_number, carrier):
            flash(
                "Carrier updated successfully. Please wait for a confirmation message.", "text-green-500")
            # Convert the new entry to email format
            convert_to_email()
            # send confirmation message
            confirmation_message()
        else:
            with open('contacts.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([phone_number, carrier])
            flash(
                "Successfully signed up. Please wait for a confirmation message.", "text-green-500")
            # Convert the new entry to email format
            convert_to_email()
            # send confirmation message
            confirmation_message()

        return redirect(url_for('index'))
    return render_template('index.html')


def confirmation_message():
    with open('email_contacts.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            recipient_email = row[0]

    smtp_server = SMTP_SERVER
    smtp_port = SMTP_PORT
    smtp_user = SMTP_USER
    smtp_password = SMTP_PASSWORD
    SUBJECT = "Confirmation Message"
    MESSAGE = "You have successfully signed up for emergency alerts."

    try:
        send_sms_via_email(recipient_email, SUBJECT, MESSAGE,
                           smtp_server, smtp_port, smtp_user, smtp_password)
    except Exception as e:
        # Remove contact from CSV if sending fails
        flash(f'Error sending confirmation message: {
            str(e)}. Please try again.', 'error')


@app.route('/send', methods=['GET', 'POST'])
# Route to display the form to send a message
def send():
    if request.method == 'POST':
        if request.form['password'] == SEND_PASSWORD:
            message = request.form['message']
            # Default subject if none provided
            subject = request.form['subject'] or 'Emergency Alert'
            smtp_server = SMTP_SERVER
            smtp_port = SMTP_PORT
            smtp_user = SMTP_USER
            smtp_password = SMTP_PASSWORD

            # Read email contacts from the CSV file
            with open('email_contacts.csv', mode='r') as infile:
                reader = csv.reader(infile)
                for row in reader:
                    recipient = row[0]
                    send_sms_via_email(recipient, subject, message, smtp_server,
                                       smtp_port, smtp_user, smtp_password)

            # Save the message content to a CSV file
            with open('sent_messages.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([message])
            flash("Message sent successfully", "text-green-500")
            return redirect(url_for('send'))
        else:
            flash("Incorrect password. Please try again.", "text-red-500")
            return redirect(url_for('send'))

    return render_template('send.html')


def is_registered(phone_number, carrier):
    # Function to check if phone number is already registered
    with open('contacts.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if phone_number == row[0] and carrier == row[1]:
                return True
    return False


def update_carrier(phone_number, carrier):
    # Function to update carrier if phone number is already registered
    with open('contacts.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if phone_number == row[0] and carrier != row[1]:
                remove_contact(phone_number)
                with open('contacts.csv', mode='a') as file:
                    writer = csv.writer(file)
                    writer.writerow([phone_number, carrier])
                return True
    return False


def remove_contact(phone_number):
    def remove_from_csv(file_name):
        lines = []
        with open(file_name, 'r') as file:
            reader = csv.reader(file)
            lines = [line for line in reader if line[0] != phone_number]
        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(lines)

    remove_from_csv('contacts.csv')
    remove_from_csv('email_contacts.csv')


def convert_to_email():
    # Function to convert phone numbers to email format
    carrier_gateways = {
        'att': 'txt.att.net',
        'verizon': 'vtext.com',
        'tmobile': 'tmomail.net',
        'boost': 'sms.myboostmobile.com',
        'cricket': 'sms.cricketwireless.net',
        'metroPCS': 'mymetropcs.com',
        'republic': 'text.republicwireless.com',
        'google': 'msg.fi.google.com',
        'uscellular': 'email.uscc.net',
        'cspire': 'cspire1.com',
        'virgin': 'vmobl.com',
        'ting': 'message.ting.com',
        'consumer': 'mailmymobile.net',
        'inland': 'inlandlink.com',
        'nextel': 'messaging.nextel.com',
        'alltel': 'message.alltel.com',
        'telus': 'msg.telus.com',
        'rogers': 'pcs.rogers.com',
        'bell': 'txt.bell.ca',
        'fido': 'fido.ca',
        'koodo': 'msg.koodomobile.com',
        'saskTel': 'sms.sasktel.com',
        'solo': 'txt.solomobile.ca',
        'pcmobile': 'txt.pcmobile.ca',
        'mts': 'text.mtsmobility.com',
        'suncom': 'tms.suncom.com',
        'viaero': 'viaerosms.com',
        'freedom': 'txt.freedommobile.ca',
        'public': 'msg.telus.com',
        'videotron': 'sms.videotron.ca',
        'eastlink': 'sms.eastlink.ca',
    }

    with open('contacts.csv', mode='r') as infile, open('email_contacts.csv', mode='w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        for row in reader:
            phone_number, carrier = row
            if carrier in carrier_gateways:
                email_address = f"{phone_number}@{carrier_gateways[carrier]}"
                writer.writerow([email_address])


def split_message(message, chunk_size=100):
    # Function to send SMS via email
    words = message.split(' ')
    chunks = []
    current_chunk = ''

    for word in words:
        if len(current_chunk) + len(word) + 1 > chunk_size:
            chunks.append(current_chunk)
            current_chunk = word
        else:
            if current_chunk:
                current_chunk += ' '
            current_chunk += word

    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def send_sms_via_email(recipient, subject, message, smtp_server, smtp_port, smtp_user, smtp_password):
    # Split the message into 100 character chunks
    chunks = split_message(message, 100)
    # Send each chunk as a separate email
    for i, chunk in enumerate(chunks):
        part_message = f"({i+1}/{len(chunks)}) {chunk}"
        msg = MIMEText(part_message)
        msg['From'] = smtp_user
        msg['To'] = recipient
        if i == 0:
            # Only include subject in the first message
            msg['Subject'] = subject

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, recipient, msg.as_string())


if __name__ == '__main__':
    app.run(debug=True)


'''
To-Do: 
- Do something about adding wrong carrier
- Add message to say if the number and carrier sends an error 
    and remove number from list.
- Add message to say if the message was not sent/errored
    
- Get email address that will be used for sending the message
- Get generated password for that email address
- Get password for sending the message

- Host on Pythonanywhere
- Integrate with St. Katherine Website
- Get it to the people
'''
