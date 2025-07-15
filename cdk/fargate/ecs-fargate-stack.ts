import {
  Stack,
  StackProps,
  Duration,
  aws_ec2 as ec2,
  aws_ecs as ecs,
  aws_ecs_patterns as ecsPatterns,
  aws_elasticloadbalancingv2 as elbv2,
  aws_certificatemanager as acm,
  aws_iam as iam,
  aws_logs as logs,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as path from 'path';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as assets from 'aws-cdk-lib/aws-s3-assets';
import * as path from 'path';

const configAsset = new assets.Asset(this, 'DashboardConfigAsset', {
  path: path.join(__dirname, '../config/dashboard_config.json'),
});

configAsset.grantRead(taskDef.taskRole);

container.addEnvironment('DASHBOARD_CONFIG_PATH', '/app/config/dashboard_config.json');

container.addMountPoints({
  containerPath: '/app/config',
  readOnly: false,
  sourceVolume: 'dashboard-config-vol'
});

taskDef.addVolume({
  name: 'dashboard-config-vol',
  host: {
    sourcePath: '/mnt/efs/config', // Or EBS mount if you persist changes
  }
});

interface FargateStackProps extends StackProps {
  vpc: ec2.IVpc;
  certificateArn: string;
  const cert = props.certificate;
}

const certRenewal = new lambda.Function(this, 'CertRenewalLambda', {
  runtime: lambda.Runtime.PYTHON_3_11,
  code: lambda.Code.fromAsset(path.join(__dirname, '../lambdas/cert_renewal_handler')),
  handler: 'cert_renewal_handler.lambda_handler',
  timeout: Duration.seconds(10),
  environment: {
    CERT_ARN: privateCertStack.certificate.certificateArn,
  },
});

export class DevGeniusFargateStack extends Stack {
  constructor(scope: Construct, id: string, props: FargateStackProps) {
    super(scope, id, props);

    const { vpc, certificateArn } = props;

    const cluster = new ecs.Cluster(this, 'DevGeniusCluster', {
      vpc,
      containerInsights: true,
    });

    const logGroup = new logs.LogGroup(this, 'DevGeniusLogGroup', {
      retention: logs.RetentionDays.ONE_WEEK,
    });

    const taskRole = new iam.Role(this, 'DevGeniusTaskRole', {
      assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
      description: 'Task role for ECS Fargate Streamlit UI',
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonBedrockFullAccess'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonS3ReadOnlyAccess'),
      ],
    });

    const taskDefinition = new ecs.FargateTaskDefinition(this, 'TaskDef', {
      memoryLimitMiB: 1024,
      cpu: 512,
      taskRole,
    });

    const container = taskDefinition.addContainer('StreamlitContainer', {
      image: ecs.ContainerImage.fromAsset(path.join(__dirname, '../../')),
      logging: ecs.LogDriver.awsLogs({
        streamPrefix: 'Streamlit',
        logGroup,
      }),
      environment: {
        STREAMLIT_SERVER_PORT: '8501',
        AWS_REGION: this.region,
      },
    });

    container.addPortMappings({
      containerPort: 8501,
    });

    const sg = new ec2.SecurityGroup(this, 'FargateSG', {
      vpc,
      description: 'Allow HTTPS inbound to ALB and ALB->ECS',
      allowAllOutbound: true,
    });

    sg.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(443), 'HTTPS from internal access');

    const lb = new elbv2.ApplicationLoadBalancer(this, 'InternalALB', {
      vpc,
      internetConnected: false,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
      securityGroup: sg,
      loadBalancerName: 'DevGeniusALB',
    });

    const cert = acm.Certificate.fromCertificateArn(this, 'Cert', certificateArn);

    const listener = lb.addListener('HTTPSListener', {
      port: 443,
      certificates: [cert],
      protocol: elbv2.ApplicationProtocol.HTTPS,
    });

    const service = new ecs.FargateService(this, 'FargateService', {
      cluster,
      taskDefinition,
      securityGroups: [sg],
      desiredCount: 1,
      assignPublicIp: false,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
      },
    });

    listener.addTargets('StreamlitTarget', {
      port: 8501,
      targets: [service],
      healthCheck: {
        path: '/',
        interval: Duration.seconds(30),
        timeout: Duration.seconds(5),
        healthyThresholdCount: 2,
        unhealthyThresholdCount: 5,
      },
    });
  }
}
