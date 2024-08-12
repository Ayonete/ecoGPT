import datetime
import boto3
import botocore.config
import os
import json
import time
import logging
import re

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Function to calculate complexity score without external libraries
def calculate_complexity_score(topic: str) -> float:
    # Factor 1: Length
    length_score = min(len(topic) / 100, 1)  # Normalize to max 1
    
    # Factor 2: Unique words ratio
    words = topic.lower().split()
    unique_words_ratio = len(set(words)) / len(words) if words else 0
    
    # Factor 3: Average word length
    avg_word_length = sum(len(word) for word in words) / len(words) if 
words else 0
    avg_word_length_score = min(avg_word_length / 10, 1)  # Normalize to 
max 1
    
    # Factor 4: Presence of technical or specialized terms
    technical_terms = ['algorithm', 'quantum', 'blockchain', 'neural', 
'genome', 'cryptocurrency']
    technical_score = sum(term in topic.lower() for term in 
technical_terms) / len(technical_terms)
    
    # Factor 5: Sentence complexity (based on punctuation)
    sentences = re.split(r'[.!?]+', topic)
    avg_sentence_length = sum(len(sentence.split()) for sentence in 
sentences) / len(sentences) if sentences else 0
    sentence_complexity = min(avg_sentence_length / 20, 1)  # Normalize to 
max 1
    
    # Calculate final score (weights can be adjusted)
    complexity_score = (
        length_score * 0.2 +
        unique_words_ratio * 0.2 +
        avg_word_length_score * 0.2 +
        technical_score * 0.2 +
        sentence_complexity * 0.2
    )
    
    return complexity_score

# Function to select the appropriate Bedrock model based on complexity
def select_model(blogtopic: str) -> str:
    complexity_score = calculate_complexity_score(blogtopic)
    logger.info(f"Complexity score: {complexity_score}")
    
    if complexity_score > 0.6:
        return "amazon.titan-text-express-v1"  # Use titan express for 
more complex topics
    else:
        return "amazon.titan-text-lite-v1"  # Use Titan lite for simpler 
topics

# Function to generate blog content using Amazon Bedrock
def blog_generate_using_bedrock(blogtopic: str) -> tuple:
    model_id = select_model(blogtopic)
    
    prompt = f""" <s>[INST]Human: Write a 200 word blog on the topic 
{blogtopic}.</s>
    Assistant: [/INST]:
"""
    
    body = {
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.5,
        "top_p": 0.9,
    }
    try:
        bedrock = boto3.client("bedrock-runtime", region_name="us-east-1",
                               
config=botocore.config.Config(read_timeout=300, retries={"max_attempts": 
3}))
        
        response = bedrock.invoke_model(body=json.dumps(body), 
modelId=model_id)
        response_content = response.get('body').read()
        response_data = json.loads(response_content)
        blog_details = response_data['generation']
        logger.info(f"Blog generated using model: {model_id}")
        return blog_details, model_id
    
    except Exception as e:
        logger.error(f"Error in generating the blog: {e}")
        return "", model_id

# Function to save the generated blog content to an S3 bucket
def save_blog_details_s3(s3_key, s3_bucket, generate_blog, model_id):
    s3 = boto3.client("s3")
    try:
        content = f"Model used: {model_id}\n\n{generate_blog}"
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=content)
        logger.info(f"Blog saved in s3 bucket {s3_bucket} with key 
{s3_key}")
    except Exception as e:
        logger.error(f"Error in saving the blog in s3: {e}")

# Main Lambda handler function
def lambda_handler(event, context):
    start_time = time.time()
    
    try:
        event = json.loads(event['body'])
        blogtopic = event['blog_topic']
    except KeyError:
        logger.error("Missing 'blog_topic' in the request body")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': "Missing 'blog_topic' in the 
request body"})
        }
    except json.JSONDecodeError:
        logger.error("Invalid JSON in the request body")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': "Invalid JSON in the request 
body"})
        }
    
    complexity_score = calculate_complexity_score(blogtopic)
    generate_blog, model_used = 
blog_generate_using_bedrock(blogtopic=blogtopic)
    
    s3_key = ""
    if generate_blog:
        current_time = 
datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        s3_key = f"blog-output/{current_time}.txt"
        s3_bucket = 'aws_bedrock_1'
        save_blog_details_s3(s3_key, s3_bucket, generate_blog, model_used)
    else:
        logger.warning(f"No blog generated. Model attempted: 
{model_used}")
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    logger.info(f"Execution time: {execution_time:.2f} seconds")
    logger.info(f"Model used: {model_used}")
    logger.info(f"Complexity score: {complexity_score}")
    logger.info(f"Memory allocated: {context.memory_limit_in_mb}MB")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Blog generated using {model_used} and saved in 
s3.',
            'execution_time': f'{execution_time:.2f} seconds',
            'complexity_score': complexity_score,
            'memory_allocated': f'{context.memory_limit_in_mb}MB'
        }),
        'headers': {
            'Content-Type': 'application/json'
        }
    }
