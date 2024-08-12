import json
import datetime
import boto3
import botocore.config
import os
import time
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def blog_generate_using_bedrock(blogtopic:str)-> str:
    prompt = f""" <s>[INST]Human: Write a 200 word blog on the topic 
{blogtopic}.</s>
    Assistant: [/INST]:
""" 
    body={
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.5,
        "top_p": 1,
    }
    try:
        bedrock=boto3.client("bedrock-runtime", region_name="us-east-1",
                             
config=botocore.config.Config(read_timeout=300,retries={"max_attempts": 
3}))
        response = bedrock.invoke_model(body=json.dumps(body), 
modelId="amazon.titan-text-express-v1")
        response_content = response.get('body').read()
        response_data=json.loads(response_content)
        print(response_data)
        blog_details=response_data['generation']
        return blog_details
    except Exception as e:
        print(f"Error in generating the blog:{e}")
        return ""

def save_blog_details_s3(s3_key, s3_bucket, generate_blog):
    s3=boto3.client("s3")
    try:
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=generate_blog)
        print(f"Blog saved in s3 bucket {s3_bucket} with key {s3_key}")
    except Exception as e:
        print(f"Error in saving the blog in s3:{e}")

def lambda_handler(event, context):
    start_time = time.time()
   
    try:
        event = json.loads(event['body'])
        blogtopic = event['blog_topic']
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing blog_topic in request 
body'}),
            'headers': {'Content-Type': 'application/json'}
        }
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON in request body'}),
            'headers': {'Content-Type': 'application/json'}
        }

    generate_blog = blog_generate_using_bedrock(blogtopic=blogtopic)
    if generate_blog:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        s3_key = f"blog-output/{current_time}.txt"
        s3_bucket = 'awsbedrock1nete'
        save_blog_details_s3(s3_key, s3_bucket, generate_blog)
    else:
        print("No blog generated")
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    logger.info(f"Execution time: {execution_time:.2f} seconds")
    logger.info(f"Model used: amazon.titan-text-express-v1")
    logger.info(f"Memory allocated: {context.memory_limit_in_mb}MB")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Blog generated and saved in s3',
            'execution_time': f'{execution_time:.2f} seconds',
            'memory_allocated': f'{context.memory_limit_in_mb}MB'
        }),
        'headers': {
            'Content-Type': 'application/json'
        }
    }
