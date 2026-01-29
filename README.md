# Orphaned-Resource-Hunter
This project provides an automated solution to identify and delete unused ("orphaned") resources across various AWS services. It's designed to help you reduce cloud costs and keep your AWS environment clean and efficient.

The Challenge: Cloud Waste:
-- Unused or forgotten resources in cloud environments. 
-- They continue to incur costs even when not in use. Example: Old EC2 instances, unattached EBS volumes, unused S3 buckets. 
-- Leads to "cloud waste" and budget overruns. 

Solution: Introducing the “Orphaned Resource Hunter”

How It Works: The Architecture:
-- Lambda Functions: Two main functions: 
         A "Scanner" that identifies resources
         A "Delete" that removes selected ones.
-- DynamoDB: A NoSQL database to store the list of orphaned resources.
-- API Gateway: Provides a secure and scalable endpoint for the frontend. 
-- Frontend UI: A simple HTML file that interacts with the API.

End-to-End Workflow
1. Scanner Lambda Runs.
2. User Access UI.
3. UI Displays Resources.
4. User Selects Resources.
5. Delete Lambda Removes the Resources.

$ Benefits of the Project:
1. Cost Reduction:- Direct Cost Saved By Deleting Orphaned Resources in Single Click.
2. Resource LifeCycle Management:- Establish a Process of Managing Resources.
3. Scalability:- Serverless Solution Deployable in Any AWS Account.
4. Automation:- Reduces the Manual Effort and Human Error.
5. Infrastructure as a Code :- Deployed using Cloud Formation.
