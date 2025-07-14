// cdk/auth/cognito-stack.ts
import { Stack, StackProps, Duration, CfnOutput } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as cognito from 'aws-cdk-lib/aws-cognito';

export class CognitoAuthStack extends Stack {
  public readonly userPool: cognito.UserPool;
  public readonly userPoolClient: cognito.UserPoolClient;
  public readonly adminGroupName = 'Admin';

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // === User Pool ===
    this.userPool = new cognito.UserPool(this, 'DevGeniusUserPool', {
      userPoolName: 'DevGeniusUserPool',
      selfSignUpEnabled: true,
      signInAliases: { email: true },
      autoVerify: { email: true },
      passwordPolicy: {
        minLength: 8,
        requireLowercase: true,
        requireUppercase: true,
        requireDigits: true,
        requireSymbols: false,
      },
      accountRecovery: cognito.AccountRecovery.EMAIL_ONLY,
    });

    // === App Client ===
    this.userPoolClient = new cognito.UserPoolClient(this, 'DevGeniusAppClient', {
      userPool: this.userPool,
      generateSecret: false,
      authFlows: {
        userPassword: true,
        userSrp: true,
      },
      oAuth: {
        flows: {
          authorizationCodeGrant: true,
        },
        callbackUrls: ['http://localhost:8501'],
        logoutUrls: ['http://localhost:8501'],
      },
    });

    // === Hosted UI Domain ===
    new cognito.UserPoolDomain(this, 'DevGeniusDomain', {
      userPool: this.userPool,
      cognitoDomain: {
        domainPrefix: 'devgenius-app',
      },
    });

    // === Admin Group ===
    new cognito.CfnUserPoolGroup(this, 'AdminGroup', {
      groupName: this.adminGroupName,
      userPoolId: this.userPool.userPoolId,
      description: 'Administrators who can access usage monitor dashboard'
    });

    // === Outputs ===
    new CfnOutput(this, 'UserPoolId', {
      value: this.userPool.userPoolId,
    });
    new CfnOutput(this, 'UserPoolClientId', {
      value: this.userPoolClient.userPoolClientId,
    });
  }
}
