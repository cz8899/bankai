// cdk/fargate/ecs-fargate-stack.ts

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
  aws_s3_assets as s3Assets,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as path from 'path';

export interface FargateStackProps extends StackProps {
  vpc: ec2.IVpc;
  certificateArn: string;
}

export class DevGeniusFargateStack extends Stack {
  constructor(scope: Construct, id: string, props: FargateStackProps) {
    super(scope, id, props);

    const { vpc, certificateArn } = props;

    // ECS Cluster
    const cluster = new ecs.Cluster(this, 'DevGeniusCluster', {
      vpc,
      containerInsights: true,
    });

    // CloudWatch Logs
    const logGroup = new logs.LogGroup(this, 'DevGeniusLogGroup', {
      retention: logs.RetentionDays.ONE_WEEK,
    });

    // Task Role
    const taskRole = new iam.Role(this, 'DevGeniusTaskRole', {
      assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
      description: 'Task role for ECS Fargate Streamlit UI',
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonBedrockFullAccess'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonS3ReadOnlyAccess'),
      ],
    });

    // Fargate Task Definition
    const taskDefinition = new ecs.FargateTaskDefinition(this, 'TaskDef', {
      memoryLimitMiB: 1024,
      cpu: 512,
      taskRole,
    });

    // Load Streamlit App (Docker build from root)
    const container = taskDefinition.addContainer('StreamlitContainer', {
      image: ecs.ContainerImage.fromAsset(path.join(__dirname, '../../')),
      logging: ecs.LogDriver.awsLogs({ streamPrefix: 'Streamlit', logGroup }),
      environment: {
        STREAMLIT_SERVER_PORT: '8501',
        AWS_REGION: this.region,
      },
    });

    container.addPortMappings({ containerPort: 8501 });

    // Security Group
    const sg = new ec2.SecurityGroup(this, 'FargateSG', {
      vpc,
      description: 'Allow HTTPS from internal sources',
      allowAllOutbound: true,
    });
    sg.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(443), 'HTTPS access');

    // Load Balancer
    const alb = new elbv2.ApplicationLoadBalancer(this, 'InternalALB', {
      vpc,
      internetFacing: false,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
      securityGroup: sg,
    });

    const cert = acm.Certificate.fromCertificateArn(this, 'Cert', certificateArn);

    const listener = alb.addListener('HTTPSListener', {
      port: 443,
      certificates: [cert],
      protocol: elbv2.ApplicationProtocol.HTTPS,
    });

    // ECS Fargate Service
    const service = new ecs.FargateService(this, 'FargateService', {
      cluster,
      taskDefinition,
      desiredCount: 1,
      assignPublicIp: false,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
      securityGroups: [sg],
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

    // === OPTIONAL: Static Config Mount (ZIP Lambda-compatible)
    const configAsset = new s3Assets.Asset(this, 'DashboardConfigAsset', {
      path: path.join(__dirname, '../config/dashboard_config.json'),
    });
    configAsset.grantRead(taskRole);
    container.addEnvironment('DASHBOARD_CONFIG_S3_URL', configAsset.s3ObjectUrl);
  }
}
