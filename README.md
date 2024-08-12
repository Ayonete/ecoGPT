<h1>Adaptive Model Selection for Energy Efficient LLM Inference in the Cloud</h1>
<h2>Overview</h2>
<p>This project focuses on optimizing the inference of Large Language Models (LLMs) deployed on AWS for energy efficiency. By leveraging adaptive model selection and serverless architecture, this solution aims to reduce power consumption while maintaining performance during inference. The primary goal is to develop a system that dynamically adjusts the computational resources based on the complexity of the input, thereby optimizing energy use.</p>
<h2>Project Components</h2>
<h3>1. <strong>Text Generation Lambda Function</strong></h3>
<p>This AWS Lambda function handles the generation of blog content using Amazon Bedrock. It selects the appropriate LLM model based on the input complexity and saves the generated content in an Amazon S3 bucket.</p>
<ul>
    <li><strong>Key Features</strong>:
        <ul>
            <li><strong>Adaptive Model Selection:</strong> Chooses between different LLM models based on the input token length.</li>
            <li><strong>Text Generation:</strong> Generates blog content using Amazon Bedrock.</li>
            <li><strong>S3 Integration:</strong> Saves the generated content in Amazon S3 for storage and retrieval.</li>
        </ul>
    </li>
</ul>
<h3>2. <strong>Resource Monitoring Lambda Function</strong></h3>
<p>This secondary Lambda function is triggered after the blog generation Lambda completes execution. It gathers CloudWatch metrics such as execution time and memory usage, calculates power consumption based on these metrics, and logs this data back into CloudWatch.</p>
<ul>
    <li><strong>Key Features</strong>:
        <ul>
            <li><strong>CloudWatch Metrics:</strong> Retrieves execution time and memory usage metrics.</li>
            <li><strong>Power Consumption Calculation:</strong> Calculates the estimated power consumption based on the gathered metrics.</li>
            <li><strong>Custom CloudWatch Metrics:</strong> Logs power consumption as a custom metric in CloudWatch for monitoring.</li>
        </ul>
    </li>
</ul>

<h2>Conclusion</h2>
<p>This project provides a scalable, energy-efficient solution for deploying LLMs in the cloud. By utilizing AWS Lambda, Amazon Bedrock, and CloudWatch, we achieve dynamic resource allocation that optimizes power consumption during inference, ensuring sustainable use of AI technologies.</p>
