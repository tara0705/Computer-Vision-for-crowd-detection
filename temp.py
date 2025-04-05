from twilio.rest import Client
def call_py():
    account_sid = 'ur acc_sid from twilio'
    auth_token = 'ur auth-token from twilio'
    message="hii"
    client = Client(account_sid, auth_token)
    call = client.calls.create(
        to="your number",  # Owner's phone number
        from_="your twilio number",  # Your Twilio phone number
        twiml=f'<Response><Say>{message}</Say></Response>'  # Message to be read out during the call
    )
    print("DONE")
    print(f"Call SID: {call.sid}")
    print("I Have Alerted The Owner")
call_py()