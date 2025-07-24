import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as s3 from 'aws-cdk-lib/aws-s3';

export interface LivekitAgentEC2Props {
  readonly envName: string;
  readonly envPrefix: string;
  readonly vpc?: ec2.IVpc;
  readonly instanceType?: ec2.InstanceType;
  readonly ssmParameterPath: string;
  readonly sourceBucket: s3.IBucket;
}

export class LivekitAgentEC2 extends Construct {
  public readonly instance: ec2.Instance;
  
  constructor(scope: Construct, id: string, props: LivekitAgentEC2Props) {
    super(scope, id);
    
    const sepHyphen = props.envPrefix ? "-" : "";
    
    // Use existing VPC or create a new one
    const vpc = props.vpc || new ec2.Vpc(this, 'LivekitAgentVpc', {
      maxAzs: 2,
      natGateways: 1,
    });
    
    // Create security group
    const securityGroup = new ec2.SecurityGroup(this, 'LivekitAgentSG', {
      vpc,
      description: 'Security group for LiveKit agent EC2 instance',
      allowAllOutbound: true,
    });
    
    // Allow SSH (for administration)
    securityGroup.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.tcp(22),
      'Allow SSH from anywhere'
    );
    
    // Create role for the EC2 instance
    const role = new iam.Role(this, 'LivekitAgentRole', {
      assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSSMManagedInstanceCore'),
      ],
    });
    
    // Add permissions to read parameters/secrets
    role.addToPolicy(new iam.PolicyStatement({
      actions: ['ssm:GetParameter', 'ssm:GetParameters'],
      resources: [`arn:aws:ssm:${cdk.Stack.of(this).region}:${cdk.Stack.of(this).account}:parameter${props.ssmParameterPath}/*`],
    }));
        
    // Create a CloudWatch log group for the agent
    const logGroup = new logs.LogGroup(this, 'LivekitAgentLogs', {
      logGroupName: `/aws/ec2/${props.envPrefix}${sepHyphen}livekit-agent`,
      retention: logs.RetentionDays.TWO_WEEKS,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });
    
    // Create the EC2 instance
    this.instance = new ec2.Instance(this, 'LivekitAgentInstance', {
      vpc,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PUBLIC, // For easy SSH access in dev
      },
      instanceType: props.instanceType || ec2.InstanceType.of(ec2.InstanceClass.T2, ec2.InstanceSize.MICRO),
      machineImage: ec2.MachineImage.latestAmazonLinux2023(),
      securityGroup,
      role,
      userData: ec2.UserData.forLinux(),
      keyName: 'livekit-agent-key', // Make sure to create this key pair in AWS console
    });
    
    // Add CloudWatch permissions
    logGroup.grantWrite(role);
    
    // Add user data to set up the agent
    const userData = this.instance.userData;
    const region = cdk.Stack.of(this).region;

    role.addToPolicy(new iam.PolicyStatement({
      actions: ['s3:GetObject', 's3:ListBucket'],
      resources: [
        props.sourceBucket.bucketArn,
        `${props.sourceBucket.bucketArn}/*`
      ]
    }));    
    
    userData.addCommands(
      'yum update -y',
      'yum install -y amazon-cloudwatch-agent docker git',
      'systemctl start docker',
      'systemctl enable docker',
      'usermod -a -G docker ec2-user',  // Add this line to grant permissions      
      
      // Clone repository (or use S3 bucket to retrieve code)
      `echo "Debug: Attempting to access bucket: ${props.sourceBucket.bucketName}"`,
      `aws s3 cp s3://${props.sourceBucket.bucketName}/backend/app/livekit_agent.py /home/ec2-user/livekit_agent.py`,
      'chmod +x /home/ec2-user/livekit_agent.py',
      
      // Create environment file
      'mkdir -p /home/ec2-user/.env',
      'cat > /home/ec2-user/.env/livekit.env << EOL',
      'LIVEKIT_API_KEY=$(aws ssm get-parameter --name \'' + props.ssmParameterPath + '/livekit/api-key\' --with-decryption --query "Parameter.Value" --output text --region ' + region + ')',
      'LIVEKIT_API_SECRET=$(aws ssm get-parameter --name \'' + props.ssmParameterPath + '/livekit/api-secret\' --with-decryption --query "Parameter.Value" --output text --region ' + region + ')',
      'LIVEKIT_URL=$(aws ssm get-parameter --name \'' + props.ssmParameterPath + '/livekit/url\' --with-decryption --query "Parameter.Value" --output text --region ' + region + ')',
      'OPENAI_API_KEY=$(aws ssm get-parameter --name \'' + props.ssmParameterPath + '/livekit/plugin/openai-api-key\' --with-decryption --query "Parameter.Value" --output text --region ' + region + ')',
      'DEEPGRAM_API_KEY=$(aws ssm get-parameter --name \'' + props.ssmParameterPath + '/livekit/plugin/deepgram-api-key\' --with-decryption --query "Parameter.Value" --output text --region ' + region + ')',
      'EOL',

      // Create Docker Compose file for livekit-agent
      'mkdir -p /home/ec2-user/livekit-agent',
      'cat > /home/ec2-user/livekit-agent/docker-compose.yml << EOL',
      'version: "3"',
      'services:',
      '  livekit-agent:',
      '    build:',
      '      context: .',
      '      dockerfile: Dockerfile',
      '    restart: always',
      '    env_file:',
      '      - ../.env/livekit.env',
      '    volumes:',
      '      - ./logs:/logs',
      'EOL',
      
      // Create Dockerfile
      'cat > /home/ec2-user/livekit-agent/Dockerfile << EOL',
      'FROM python:3.13-slim',
      'WORKDIR /app',
      'RUN pip install poetry && \\',
      '    poetry config virtualenvs.create false',
      'COPY requirements.txt .',
      'RUN pip install -r requirements.txt',
      'COPY livekit_agent.py .',
      'CMD ["python", "livekit_agent.py", "start"]',
      'EOL',
      
      // Create requirements.txt
      'cat > /home/ec2-user/livekit-agent/requirements.txt << EOL',
      'livekit-agents>=1.1.5',
      'livekit-plugins-openai>=1.1.5',
      'livekit-plugins-deepgram>=1.1.5',
      'livekit-plugins-silero>=1.1.5',
      'livekit-agents[mcp]>=1.1.5',
      'EOL',
      
      // Copy agent script
      'cp /home/ec2-user/livekit_agent.py /home/ec2-user/livekit-agent/',
      
      // Create directory for logs
      'mkdir -p /home/ec2-user/livekit-agent/logs',
      
      // Build and start the Docker container
      'cd /home/ec2-user/livekit-agent',
      'curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose',
      'chmod +x /usr/local/bin/docker-compose',
      'docker-compose build',
      'docker-compose up -d',

      // For production use, keep the systemd service as it adds reliability with minimal overhead. For dev/testing, Docker's restart policy is probably sufficient.
      // Create systemd service to ensure Docker and the container start on boot
      'cat > /etc/systemd/system/livekit-agent.service << EOL',
      '[Unit]',
      'Description=LiveKit Agent Service',
      'After=docker.service',
      'Requires=docker.service',
      '',
      '[Service]',
      'Type=oneshot',
      'RemainAfterExit=yes',
      'WorkingDirectory=/home/ec2-user/livekit-agent',
      'ExecStart=/usr/bin/docker-compose up -d',
      'ExecStop=/usr/bin/docker-compose down',
      'TimeoutStartSec=0',
      '',
      '[Install]',
      'WantedBy=multi-user.target',
      'EOL',
      'systemctl daemon-reload',
      'systemctl enable livekit-agent',      

      // Set up CloudWatch agent for logs
      'cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << EOL',
      '{',
      '  "logs": {',
      '    "logs_collected": {',
      '      "files": {',
      '        "collect_list": [',
      '          {',
      '            "file_path": "/var/lib/docker/containers/*/*.log",',
      '            "log_group_name": "' + logGroup.logGroupName + '",',
      '            "log_stream_name": "{instance_id}-livekit-agent",',
      '            "timestamp_format": "%Y-%m-%dT%H:%M:%S.%fZ"',
      '          }',
      '        ]',
      '      }',
      '    }',
      '  }',
      '}',
      'EOL',
      'systemctl restart amazon-cloudwatch-agent',
    );
    
    // Add outputs
    new cdk.CfnOutput(this, 'InstanceId', {
      value: this.instance.instanceId,
    });
    
    new cdk.CfnOutput(this, 'InstancePublicIp', {
      value: this.instance.instancePublicIp,
    });
    
    new cdk.CfnOutput(this, 'LogGroupName', {
      value: logGroup.logGroupName,
    });
    
    // Add tags
    cdk.Tags.of(this).add('AppManagerCFNStackKey', 'LiveKitAgent');
    cdk.Tags.of(this).add('Name', `${props.envPrefix}${sepHyphen}livekit-agent`);  
  }
}