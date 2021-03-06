import json
from Instagram import InstagramAPI
import time, random, os, sys, datetime
import boto3

dynamoClient = boto3.resource('dynamodb')
accountTable = dynamoClient.Table(os.environ['accountTable'])
scannedTable = dynamoClient.Table(os.environ['scannedTable'])
usersTable = dynamoClient.Table(os.environ['usersTable'])

def comment(event, context):
    username = os.environ['username']
    password = os.environ['password']

    RandomItem = usersTable.scan(
        ProjectionExpression = "pk"
    )

    account = accountTable.get_item(
        Key={
        'date': str(datetime.datetime.now().date()), 'username': username
        }
    ) 
    try:
        print(account['Item'])
    except KeyError:
        Item = {
            'date': str(datetime.datetime.now().date()),
            'username': username,
            'followed': 0,
            'comments': 0,
            'unfollowed': 0,
            'likes': 0,
            'blocked': False
        }
        accountTable.put_item(Item=Item)
        return
    
    if account['Item']['comments'] >= int(os.environ['rateLimitsComment']):
        return
    else:
        api = InstagramAPI(username, password)
        api.login()
        api.getUserFeed(int(random.choice(RandomItem['Items'])['pk']), maxid='', minTimestamp=None)
        
        try:
            api.comment(random.choice(api.LastJson['items'])['id'], 'nice pic!')
            response = accountTable.update_item(
                Key={
                    'date': str(datetime.datetime.now().date()), 'username': username
                },
                AttributeUpdates={
                    'comments': {
                        'Value': 1,
                        'Action': 'ADD'
                    }
                }
            )
        except:
            pass