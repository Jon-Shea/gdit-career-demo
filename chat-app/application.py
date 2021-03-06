import boto3
import json
from datetime import datetime
from termcolor import cprint


#--------------Modify-Me---------------
group_id = 2
write_language = "auto"
read_language = "french"
#--------------------------------------


#Static resources/variables
account_id = boto3.client('sts').get_caller_identity().get('Account')
region = "us-east-2"
sns_topic_arn = "arn:aws:sns:{}:{}:demo-topic".format(region, account_id)
sqs_queue_url = "https://sqs.{}.amazonaws.com/{}/demo-queue-{}".format(region, account_id, group_id)
sns_resource = boto3.resource("sns", region_name=region)
sqs_resource = boto3.resource("sqs", region_name=region)
translate_client = boto3.client("translate", region_name=region)

#convert readable language to the AWS language code
language_mapping = {
    "auto": "auto",
    "english": "en",
    "french": "fr",
    "german": "de",
    "spanish": "es",
    "chinese": "zh",
    "hebrew": "he"
}
write_language_code = language_mapping[write_language]
read_language_code = language_mapping[read_language]


def write_to_topic(message_json):
    '''Writes a given message to the SNS topic
    
    message_json -- string containing the JSON-representation of the message
    '''
    topic = sns_resource.Topic(sns_topic_arn)
    
    try:
        topic.publish(TopicArn=sns_topic_arn, Message=message_json)
    except Exception as error:
        return error

    return None


def pull_from_queue(timeout=1):
    '''Attempts to read a message from the SQS queue. Times out after <timeout>

    timeout -- how long to wait for a message to become available
    '''
    queue = sqs_resource.Queue(sqs_queue_url)

    messages = queue.receive_messages(MaxNumberOfMessages=1, WaitTimeSeconds=timeout)

    if len(messages) == 0:
        return None

    #Get the message
    message = messages[0]

    #Delete the message from the queue
    entries = [{'Id': message.message_id, 'ReceiptHandle': message.receipt_handle}]
    queue.delete_messages(Entries=entries)

    #Return the message body
    body = json.loads(message.body)
    published_message = body['Message']

    return published_message


def write_action():
    '''Prompts the user for a message to write, and writes it to SNS

    '''
    message = raw_input("Please enter the message you would like to send:\n\t")

    timestamp = str(datetime.now())

    #Create a dictionary describing the message and it's metadata
    message_dict = {
        "message": message,
        "group_id": group_id,
        "timestamp": timestamp,
        "language": write_language_code
    }

    #Dump the dictionary to a JSON representation string
    message_json = json.dumps(message_dict)

    error = write_to_topic(message_json)
    if error:
        print("Error writing to topic {} - {}".format(sns_topic_arn, error))

    return


def print_message(message_dict):
    '''Prints a given message to the screen

    message_dict -- dictionary describing the message
    '''
    message = message_dict["message"]
    group_id = message_dict["group_id"]
    timestamp = message_dict["timestamp"]

    cprint("[group-{}] @{}: {}".format(group_id, timestamp, message), "green")


def translate_message(message, source_language, target_language):
    '''Translates a given message from the source language to the target language

    message -- text to translate
    source_language -- language code for the source language
    target_language -- language code for the target language
    '''
    response = translate_client.translate_text(Text=message, SourceLanguageCode=source_language, TargetLanguageCode=target_language)

    translated_message = response['TranslatedText']

    return translated_message


def read_action():
    '''Attempts to read a message from the SQS queue, translate it, and print it to the screen

    '''
    message_json = pull_from_queue()
    if not message_json:
        return False

    try:
        message_dict = json.loads(message_json)

        if message_dict['language'] != read_language_code:
            translated_message = translate_message(message_dict["message"], message_dict["language"], read_language_code)
            message_dict["message"] = translated_message
            message_dict["language"] = read_language_code

        print_message(message_dict)
    except Exception as error:
        print("Error - {} - {}".format(message_json, error))

    return True


def read_all_action():
    '''Attempts to read all available messages from the SQS queue

    '''
    while True:
        messages_left = read_action()
        if not messages_left:
            break

    return


if __name__ == "__main__":

    #mapping between user input and the function to call
    actions = {
        'write': write_action,
        'read': read_all_action
    }

    print("Allowed actions are {}".format(list(actions.keys())))

    while True:
        #Prompt the user for the action to take
        response = raw_input("Which action would you like to take?: ")
        if response not in actions.keys():
            print("Allowed actions are {}".format(list(actions.keys())))
            continue

        #Execute the requested action
        actions[response]()
