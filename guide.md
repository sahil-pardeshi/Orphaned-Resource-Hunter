Step-by-Step Guide: Deploying the Orphaned Resource Hunter in Your AWS Account

This guide explains how to use this GitHub repository to deploy the Orphaned Resource Hunter application to your own AWS account using a CloudFormation template and GitHub Actions.

Prerequisites

  * An AWS account with Administrator access.
  * A GitHub account.
  * Git installed on your local machine.



Step 1: Fork and Clone the Repository

First, you need to create a copy of this repository in your own GitHub account.

1.  Navigate to the repository on GitHub.
2.  Click the **"Fork"** button in the top-right corner.
3.  On your newly forked repository, click the green **"Code"** button and copy the HTTPS URL.
4.  Open your terminal and clone the repository to your local machine:
    ```bash
    git clone [your-forked-repo-url]
    ```
5.  Navigate into the project directory:
    ```bash
    cd Orphaned-Resource-Hunter
    ```

Step 2: Configure AWS Credentials

To allow GitHub Actions to deploy resources in your AWS account, you need to set up a new IAM user and store the credentials securely as GitHub secrets.

Create an IAM User in AWS

1.  Log in to your AWS Management Console.
2.  Navigate to the **IAM** service.
3.  Go to **Users** and click **"Add users"**.
4.  Give the user a name (e.g., `github-actions-deployer`).
5.  Select **"Access key - Programmatic access"** and click **"Next: Permissions"**.
6.  Attach the **"AdministratorAccess"** policy. This provides the necessary permissions for the CloudFormation stack to create all the required resources.
7.  Click **"Next: Tags"**, then **"Next: Review"**, and finally **"Create user"**.
8.  **Important:** Copy the `Access key ID` and the `Secret access key` shown on the screen. **You will not be able to see the secret key again.**

Add Credentials to GitHub Secrets

1.  Go to your forked repository on GitHub.
2.  Navigate to **Settings** \> **Secrets and variables** \> **Actions**.
3.  Click **"New repository secret"**.
4.  Create two new secrets:
      * **Name:** `AWS_ACCESS_KEY_ID`
      * **Value:** Paste the Access key ID you copied from AWS.
      * **Name:** `AWS_SECRET_ACCESS_KEY`
      * **Value:** Paste the Secret access key you copied from AWS.



Step 3: Deploy the CloudFormation Stack

The CloudFormation template (`OrphanedResourceHunter.yaml`) and the GitHub Actions workflow (`deploy.yml`) are already configured to deploy the project.

1.  **Commit and Push:** Make a small change to the `README.md` file, save it, and commit it to your repository. Then push the changes to GitHub.
    ```bash
    git add .
    git commit -m "Initial commit to trigger deployment"
    git push origin main
    ```
2.  **Monitor the Deployment:** Go to the **Actions** tab in your GitHub repository. You will see a workflow run in progress.
3.  Click on the workflow run to see the deployment logs. The `Deploy CloudFormation stack` step will show the progress of your CloudFormation deployment.
4.  **Verify in AWS:** Once the workflow completes, go to the **CloudFormation** service in your AWS console. You will see a new stack named `OrphanedResourceHunterStack` in the `CREATE_COMPLETE` status.
5.  You can also check the **Lambda** and **DynamoDB** services to confirm the new resources have been created.

Your project is now successfully deployed and running in your AWS account. You can find the API Gateway endpoint URL in the **Outputs** tab of your CloudFormation stack.
