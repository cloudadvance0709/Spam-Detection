import json
import requests
import random
import boto3
from email.parser import BytesParser, Parser
from email.policy import default

##################################
endpoint = 'https://5295t8jcs0.execute-api.us-east-1.amazonaws.com/Prod'
##################################

def get_msg_body(msg):
    type = msg.get_content_maintype()

    if type == 'multipart':
        for part in msg.get_payload():
            if part.get_content_maintype() == 'text':
                return part.get_payload()
    elif type == 'text':
        return msg.get_payload()

def lambda_handler(event, context):
    
    s3_bucket = event['Records'][0]['s3']['bucket']['name']
    s3_key = event['Records'][0]['s3']['object']['key']
    
#    s3_bucket = 'hw3-storemails'
#    s3_key = '097caauj2ee2puftdrlohllf5748p70e1seovc81'
    
    client = boto3.client('s3')
    data = client.get_object(Bucket=s3_bucket, Key=s3_key)
    contents = data['Body'].read()
    
    msg = Parser(policy=default).parsestr(contents.decode('ascii'))
    frm = msg['from']
    to = msg['to']
    time = msg['date']
    subject = msg['subject']
    
    body = get_msg_body(msg)
    body = " ".join(body.split()).strip()
    
    print(time)
    
    r = requests.post(endpoint, data = {'data':body}, headers = {'Content-Type': 'application/x-www-form-urlencoded'})
    r = json.loads(r.text)
    
    print(r)

    label = int(float(r['predicted_label']))
    if label == 1:
        label = 'SPAM'
    else: label = 'HAM'
    p = float(r['predicted_probability'])
    
    print(label, p)
    
    if len(body)>250: body = body[0:250]
    
    return_msg = 'We received your email sent at ' +\
        time + 'with the subject \'' + subject +\
        '\'.\n\nHere is a 240 character sample of the email body:\n\n' +\
        body + '\n\nThe email was categorized as ' +  label +\
        ' with a ' + str(p) + ' % confidence.'

    client = boto3.client('ses')

    status = client.send_email(
        Source='hamspamreply@hw3tiz2102.xyz',
        Destination={
            'ToAddresses': [
                frm,
            ],
        },
        Message={
            'Subject': {
                'Data': 'Ham/Spam Analysis'
                
                },
            'Body': {
                'Text': {
                    'Data': return_msg,
                }
            }
        },
    )
    
    print(status)
    
    return {
        'statusCode': 200,
        'body': json.dumps('LF2 successfull!')
    }
