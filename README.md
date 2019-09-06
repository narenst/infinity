# INFINITY

Fully managed Spot GPU machines for ML development. Infinite power at minimal cost.

## Demos

How to spin up a Spot instance and attach an EBS volume (90 sec video)

[![Demo](https://img.youtube.com/vi/W3K1U-OZm8s/0.jpg)](https://www.youtube.com/watch?v=W3K1U-OZm8s "Infinity Spot Instance")

# Installation

Infinity is fully a command line tool. To install infinity from GitHub master branch:

    pip install git+https://github.com/narenst/infinity.git@v0.3#egg=infinity

_Note: Infinity requires Python3_

# How to use

Infinity has three cli tools for managing different parts of your workflow.

## infinity

Use the `infinity` cli tool to create and manage ML development machines.

### Create new Spot instance

To spin up a new spot machine with a *Tesla K-80* GPU in your AWS region:

    infinity create --spot

If you would like to change the GPU to a *Tesla V-100*:

    infinity create --spot --instance-type p3.2xlarge

Spot instances can be preempted by AWS if they have high demand for that instance type. You can switch to on-demand instances to avoid preemption.

    infinity create --on-demand --instance-type p2.xlarge

### Manage instance

To view the instances you have created and their IDs:

    $ infinity list

    ID                   NAME              MACHINE TYPE    TYPE       IP      DISK  STATUS
    -------------------  ----------------  --------------  ---------  ----  ------  --------
    i-03819f07f644dfd1e  advanced-nlp-dev  p2.xlarge       on-demand            75  stopped

Use the `start` and `stop` commands to turn on and off the machines

    $ infinity start <ID>

    Starting instance now...
    Waiting for the instance to be up and running...
    Machine is started

The stop command works only for on-demand instances:

    $ infinity stop <ID>

    Stopping instance now...
    Waiting for the instance to be stopped...
    Machine is stopped

For spot instances, you have to destroy the instance to stop it.

    $ infinity destroy <ID>

    Are you sure you want to destroy the machine? This is irrrecoverable. And you have to chosen to delete the root disk. [y/N]: y
    Destroying instance now...
    Removing alerts

You can update the specifications of the machine by using the update command

    $ infinity update <ID> --name advanced-nlp-dev --disk --type t3.large --size 100

    Updating instance name to: advanced-nlp-dev...
    Updating disk size to: 100...
    Disk is currently in modifying state. It may take a few minutes for the size change to finish
    Updating instance type to: t3.large...

### SSH and Jupyter Lab

When the instance is running, use the SSH command to login to the machine

    infinity ssh <ID>

The default machine image contains the latest versions of Tensorflow and PyTorch installed using Conda. Use `tmux` to run long running scripts and you can connect back any time to monitor progress.

Use the jupyter command to setup port forwarding for Jupyter interface. You can now access Jupyter running on the Infinity machine with a http://localhost:8888 endpoint

    infinity jupyter <ID>

Note: This does not start jupyter on the infinity machine. You need to do that yourselves using the `infinity ssh` command.

## infinity-volume

Use the `infinity-volume` cli tool manages EBS volumes and attach/detach them to instances.

To create a new volume, you need to specify either the Availability Zone or a reference instance ID, and infinity will use the same Availability Zone as that instance.

    infinity-volume create --reference-instance-id <INSTANCE_ID> --size 200

You can use volumes to store large datasets and attach them to any instance as its secondary volume. This volume is available at `/data` path on the instance.

_Note: you can only attach the volume to instance in the same availability zone._

    $ infinity-volume attach <VOLUME_ID> --instance-id <INSTANCE_ID>
    Attaching volume to the instance...
    Volume successfully attached to instance

_Note: You can attach a volume to only one instance at a time. And an instance can have only one secondary volume attached to it._

To detach a volume from its instance:

    $ infinity-volume detach
    Detaching volume from instance...
    Volume successfully detached from instance

_Note: You can only detach an instance when it is in stopped state_

## Manage volumes

You can easily manage volumes with these commands:

    infinity-volume list
    infinity-volume destroy <VOLUME_ID>
    infinity-volume update <VOLUME_ID> --name cifar-100 --size 100

## infinity-tools

The `infinity-tools` cli has some helpful tools to select the AWS region and instance type for your projects.

### AWS machine quota

AWS has default limits on which EC2 machine types you are allowed to use. And you may need to request a quota increase for some machine types. Ex: the GPU machine type `p2.xlarge` is not available by default. For cases when you need to request quota increase, use the quota command

    infinity-tools quota --instance-type p2.xlarge
    infinity-tools quota --instance-type p2.xlarge --increase-to 1

This will submit a new quota increase request to Amazon. You should receive an email on the progress of this request. It will take between 30 minutes to 24 hours for the quota increase to be approved.

### AWS spot instance prices

AWS instances are priced differently across different regions. And spot prices change even between availability zones in the same region. You can use the `price` command to see the real-time prices of instances across all AWS regions where that instance is available:

    infinity-tools price --instance-type p2.xlarge

    Getting On-demand prices across regions ...
    Getting frequency of interruptions for spot instances ...
    Getting real-time price of Spot instances ...
    +----------------+---------------------+-------------------------+--------------------+------------------------+
    | REGION         | AVAILABILITY ZONE   |   ON-DEMAND PRICE (USD) |   SPOT PRICE (USD) |  FREQ OF INTERRUPTION  |
    |----------------+---------------------+-------------------------+--------------------+------------------------|
    | ap-south-1     | ap-south-1a         |                   1.718 |             0.5266 |          >20%          |
    | ap-south-1     | ap-south-1b         |                   1.718 |             0.5989 |          >20%          |
    |                |                     |                         |                    |                        |
    | ap-southeast-1 | ap-southeast-1a     |                   1.718 |             0.6016 |          <5%           |
    | ap-southeast-1 | ap-southeast-1b     |                   1.718 |             0.5154 |          <5%           |
    |                |                     |                         |                    |                        |
    | us-west-2      | us-west-2a          |                   0.9   |             0.2885 |         15-20%         |
    | us-west-2      | us-west-2b          |                   0.9   |             0.2873 |         15-20%         |
    | us-west-2      | us-west-2c          |                   0.9   |             0.2709 |         15-20%         |
    |                |                     |                         |                    |                        |
    +----------------+---------------------+-------------------------+--------------------+------------------------+

This command also shows the frequency of your spot instance getting interrupted (provided by AWS). You can use this to identify the best region to spin up AWS instances.

# Setup Infinity

This section covers how to setup Infinity before running it for the first time.

## SSH Key

Infinity sets up cloud machines. So you will need SSH keys to login to the machine. If you do not already have an SSH key pair or would like to create a new key pair for Infinity, follow the instructions [here](https://help.github.com/en/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) for your operating system.

## AWS account

You need an AWS account to use Infinity. The tool will setup AWS EC2 machines as your ML development machines. If you do not have an account already, follow instructions [here](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/).

## AWS Credentials

With you AWS account, you need to create an IAM account and security credentials. You can learn how to do this [here](https://aws.amazon.com/premiumsupport/knowledge-center/create-access-key/). Make sure the user has the following policies (permissions):

    AmazonEC2FullAccess
    AWSCloudFormationFullAccess
    AmazonSNSFullAccess
    CloudWatchFullAccess

To run the `infinity-tools` commands successfully, you also need to add these permissions:

    ServiceQuotasFullAccess
    AWSPriceListServiceFullAccess


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

Video showing how to setup Infinity and manage instances:

[![Demo](https://img.youtube.com/vi/lXEeteH3-So/0.jpg)](https://www.youtube.com/watch?v=lXEeteH3-So "Infinity Demo")

## Analytics

Infinity uses anonymized usage analytics to learn how the tool is used. More info on this is available in the [analytics page](./infinity/analytics/README.md)
