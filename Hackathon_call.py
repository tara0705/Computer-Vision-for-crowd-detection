from twilio.rest import Client

# Your Twilio account SID and auth token
account_sid = 'your twilio account sid'
auth_token = 'your tiwilo auth_token'

# Create a Twilio client instance
client = Client(account_sid, auth_token)

def make_call(to_phone_number, from_phone_number, message):
    """
    Initiates a call to the given phone number with a specified message.
    """
    # Create and initiate the call using Twilio API
    call = client.calls.create(
        to=to_phone_number,  # Owner's phone number
        from_=from_phone_number,  # Your Twilio phone number
        twiml=f'<Response><Say>{message}</Say></Response>'  # Message to be read out during the call
    )
    # Print out the Call SID for reference
    print(f"Call SID: {call.sid}")

# Main entry point for the script
if __name__ == "__main__":
    # Specify the recipient and sender phone numbers, and the message to be delivered
    to_phone_number = 'receiver phone number'  # Recipient phone number
    from_phone_number = 'your twilio phone number'  # Your Twilio phone number
    message = "Alert! An unrecognized person has been detected by the CCTV camera. Please redress immediately."

    # Make the call with the provided parameters
    make_call(to_phone_number, from_phone_number, message)
