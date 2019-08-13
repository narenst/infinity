# INFINITY

Machine Learning dev boxes in the cloud. Infinite power on-demand.

## Demo

Video showing how to use Infinity:

[![Demo](https://img.youtube.com/vi/lXEeteH3-So/0.jpg)](https://www.youtube.com/watch?v=lXEeteH3-So "Infinity Demo")

# Installation and Setup

Infinity is fully a command line tool. To install infinity from GitHub master branch:

    pip install git+https://github.com/narenst/infinity.git#egg=infinity

## SSH Key

Infinity sets up cloud machines. So you will need SSH keys to login to the machine. If you do not already have an SSH key pair or would like to create a new key pair for Infinity, follow the instructions [here](https://help.github.com/en/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) for your operating system.

## AWS account

You need an AWS account to use Infinity. The tool will setup AWS EC2 machines as your ML development machines. If you do not have an account already, follow instructions [here](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/).

## AWS Credentials

With you AWS account, you need to create an IAM account and security credentials. You can learn how to do this [here](https://aws.amazon.com/premiumsupport/knowledge-center/create-access-key/). Make sure the user has the following policies (permissions):

    AmazonEC2FullAccess
    AWSCloudFormationFullAccess
    ServiceQuotasFullAccess

Then save the new user's Access Key ID and Secret Access Key in a newly created credentials file at `~/.aws/credentials`. The format of the file is below:

    [default]
    aws_access_key_id = ********************
    aws_secret_access_key = ****************************************

These credentials will be used by the infinity command line tool.

## Setup Infinity

Before you run Infinity for the first time, you need to setup the tool in your AWS account. You have to do this for each AWS region you use Infinity on. Select the AWS region based on geographical proximity to you and various machine types offered in that region.

To setup infinity in the `us-east-2` region, you need to run:

    infinity setup us-east-2 --ssh-public-key-path ~/.ssh/id_rsa.pub --ssh-private-key-path ~/.ssh/id_rsa

Use the SSH key path you created in the previous step. This will spin up a new CloudFormation stack that setups a secure VPC, Subnet and Security Group. You can view the CloudFormation file in the `~/.infinity` directory. You can also use any other cloud formation file in the setup step here. This newly created network will be used to launch infinity machines.

# Manage machines

Use infinity commands to create, manage and destroy development machines. The update command can change the machine name, increase disk size and change the machine type.

    infinity list
    infinity create
    infinity destroy <ID>
    infinity update <ID>

Use the start / stop commands to turn on / off the machine.

    infinity stop <ID>
    infinity start <ID>

## Connect to the machine

Use the SSH command to login to the machine

    infinity ssh <ID>

The default machine image contains the latest versions of Tensorflow and PyTorch installed using Conda. Use `tmux` to run long running scripts and you can connect back any time to monitor progress.

Use the jupyter command to setup port forwarding for Jupyter interface. You can now access Jupyter running on the Infinity machine with a http://localhost:8888 endpoint

    infinity jupyter <ID>

Note: This does not start jupyter on the infinity machine. You need to do that yourselves using the `infinity ssh` command.

# AWS machine quota

AWS has default limits on which EC2 machine types you are allowed to use. And you may need to request a quota increase for some machine types. Ex: the GPU machine type `p2.xlarge` is not available by default. For cases when you need to request quota increase, use the quota command

    infinity quota --instance-type p2.xlarge
    infinity quota --instance-type p2.xlarge --increase-to 1

This will submit a new quota increase request to Amazon. You should receive an email on the progress of this request. It will take between 30 minutes to 24 hours for the quota increase to be approved.
