import { CfnOutput, RemovalPolicy, StackProps, IgnoreMode } from "aws-cdk-lib";
import {
  BlockPublicAccess,
  Bucket,
  BucketEncryption,
  HttpMethods,
  ObjectOwnership,
} from "aws-cdk-lib/aws-s3";
import { Distribution } from "aws-cdk-lib/aws-cloudfront";
import { Construct } from "constructs";
import { Auth } from "./constructs/auth";
import { Api } from "./constructs/api";
import { Database } from "./constructs/database";
import { Frontend } from "./constructs/frontend";
import { WebSocket } from "./constructs/websocket";
import { LivekitAgentEC2 } from './constructs/livekit-agent-ec2';

import * as cdk from "aws-cdk-lib";
import { Embedding } from "./constructs/embedding";
import { UsageAnalysis } from "./constructs/usage-analysis";
import { TIdentityProvider, identityProvider } from "./utils/identity-provider";
import { ApiPublishCodebuild } from "./constructs/api-publish-codebuild";
import { WebAclForPublishedApi } from "./constructs/webacl-for-published-api";
import * as s3deploy from "aws-cdk-lib/aws-s3-deployment";
import * as iam from "aws-cdk-lib/aws-iam";
import * as logs from "aws-cdk-lib/aws-logs";
import * as path from "path";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import { BedrockCustomBotCodebuild } from "./constructs/bedrock-custom-bot-codebuild";
import { BotStore, Language } from "./constructs/bot-store";
import { Duration } from "aws-cdk-lib";

export interface BedrockAIAssistantStackProps extends StackProps {
  readonly envName: string;
  readonly envPrefix: string;
  readonly bedrockRegion: string;
  readonly webAclId: string;
  readonly identityProviders: TIdentityProvider[];
  readonly userPoolDomainPrefix: string;
  readonly publishedApiAllowedIpV4AddressRanges: string[];
  readonly publishedApiAllowedIpV6AddressRanges: string[];
  readonly allowedSignUpEmailDomains: string[];
  readonly autoJoinUserGroups: string[];
  readonly selfSignUpEnabled: boolean;
  readonly enableIpV6: boolean;
  readonly documentBucket: Bucket;
  readonly enableRagReplicas: boolean;
  readonly enableBedrockCrossRegionInference: boolean;
  readonly enableLambdaSnapStart: boolean;
  readonly enableBotStore: boolean;
  readonly enableBotStoreReplicas: boolean;
  readonly botStoreLanguage: Language;
  readonly tokenValidMinutes: number;
  readonly alternateDomainName?: string;
  readonly hostedZoneId?: string;
  readonly devAccessIamRoleArn?: string;
  // Add LiveKit props
  readonly enableLivekit?: boolean;  
  readonly livekitApiKey?: string;
  readonly livekitApiSecret?: string; 
  readonly livekitUrl?: string;
}

export class BedrockAIAssistantStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: BedrockAIAssistantStackProps) {
    super(scope, id, {
      description: "Bedrock AI Assistant Stack",
      ...props,
    });

    // Add AppManagerCFNStackKey tag for cost tracking
    cdk.Tags.of(this).add('AppManagerCFNStackKey', 'BedrockAIAssistant')

    const sepHyphen = props.envPrefix ? "-" : "";
    const idp = identityProvider(props.identityProviders);

    const accessLogBucket = new Bucket(this, "AccessLogBucket", {
      encryption: BucketEncryption.S3_MANAGED,
      blockPublicAccess: BlockPublicAccess.BLOCK_ALL,
      enforceSSL: true,
      removalPolicy: RemovalPolicy.DESTROY,
      objectOwnership: ObjectOwnership.OBJECT_WRITER,
      autoDeleteObjects: true,
    });

    // Bucket for source code
    const sourceBucket = new Bucket(this, "SourceBucketForCodeBuild", {
      encryption: BucketEncryption.S3_MANAGED,
      blockPublicAccess: BlockPublicAccess.BLOCK_ALL,
      enforceSSL: true,
      removalPolicy: RemovalPolicy.DESTROY,
      objectOwnership: ObjectOwnership.OBJECT_WRITER,
      autoDeleteObjects: true,
      serverAccessLogsBucket: accessLogBucket,
      serverAccessLogsPrefix: "SourceBucketForCodeBuild",
    });
    new s3deploy.BucketDeployment(this, "SourceDeploy", {
      sources: [
        s3deploy.Source.asset(path.join(__dirname, "../../"), {
          ignoreMode: IgnoreMode.GIT,
          exclude: [
            "**/node_modules/**",
            "**/dist/**",
            "**/dev-dist/**",
            "**/.venv/**",
            "**/__pycache__/**",
            "**/cdk.out/**",
            "**/.vscode/**",
            "**/.DS_Store/**",
            "**/.git/**",
            "**/.github/**",
            "**/.mypy_cache/**",
            "**/examples/**",
            "**/docs/**",
            "**/.env",
            "**/.env.local",
            "**/.gitignore",
            "**/test/**",
            "**/tests/**",
            "**/backend/embedding_statemachine/pdf_ai_ocr/**",
            "**/backend/guardrails/**",
          ],
        }),
      ],
      destinationBucket: sourceBucket,
      logRetention: logs.RetentionDays.THREE_MONTHS,
    });
    // CodeBuild used for api publication
    const apiPublishCodebuild = new ApiPublishCodebuild(
      this,
      "ApiPublishCodebuild",
      {
        sourceBucket,
        envName: props.envName,
        envPrefix: props.envPrefix,
        bedrockRegion: props.bedrockRegion,
      }
    );
    // CodeBuild used for KnowledgeBase
    const bedrockCustomBotCodebuild = new BedrockCustomBotCodebuild(
      this,
      "BedrockKnowledgeBaseCodebuild",
      {
        sourceBucket,
        envName: props.envName,
        envPrefix: props.envPrefix,
        bedrockRegion: props.bedrockRegion,
      }
    );

    const frontend = new Frontend(this, "Frontend", {
      accessLogBucket,
      webAclId: props.webAclId,
      enableIpV6: props.enableIpV6,
      alternateDomainName: props.alternateDomainName,
      hostedZoneId: props.hostedZoneId,
    });

    const auth = new Auth(this, "Auth", {
      origin: frontend.getOrigin(),
      userPoolDomainPrefixKey: props.userPoolDomainPrefix,
      idp,
      allowedSignUpEmailDomains: props.allowedSignUpEmailDomains,
      autoJoinUserGroups: props.autoJoinUserGroups,
      selfSignUpEnabled: props.selfSignUpEnabled,
      tokenValidity: Duration.minutes(props.tokenValidMinutes),
    });
    const largeMessageBucket = new Bucket(this, "LargeMessageBucket", {
      encryption: BucketEncryption.S3_MANAGED,
      blockPublicAccess: BlockPublicAccess.BLOCK_ALL,
      enforceSSL: true,
      removalPolicy: RemovalPolicy.DESTROY,
      objectOwnership: ObjectOwnership.OBJECT_WRITER,
      autoDeleteObjects: true,
      serverAccessLogsBucket: accessLogBucket,
      serverAccessLogsPrefix: "LargeMessageBucket",
    });

    const database = new Database(this, "Database", {
      // Enable PITR to export data to s3
      pointInTimeRecovery: true,
    });

    // Custom Bot Store
    let botStore = undefined;
    if (props.enableBotStore) {
      botStore = new BotStore(this, "BotStore", {
        envPrefix: props.envPrefix,
        botTable: database.botTable,
        conversationTable: database.conversationTable,
        language: props.botStoreLanguage,
        enableBotStoreReplicas: props.enableBotStoreReplicas,
      });
    }

    const usageAnalysis = new UsageAnalysis(this, "UsageAnalysis", {
      envPrefix: props.envPrefix,
      accessLogBucket,
      sourceDatabase: database,
    });

    const backendApi = new Api(this, "BackendApi", {
      envName: props.envName,
      envPrefix: props.envPrefix,
      database,
      auth,
      bedrockRegion: props.bedrockRegion,
      documentBucket: props.documentBucket,
      apiPublishProject: apiPublishCodebuild.project,
      bedrockCustomBotProject: bedrockCustomBotCodebuild.project,
      usageAnalysis,
      largeMessageBucket,
      enableBedrockCrossRegionInference:
        props.enableBedrockCrossRegionInference,
      enableLambdaSnapStart: props.enableLambdaSnapStart,
      openSearchEndpoint: botStore?.openSearchEndpoint,
      // Add LiveKit config
      enableLivekit: props.enableLivekit || false,
      livekitApiKey: props.livekitApiKey,
      livekitApiSecret: props.livekitApiSecret,
      livekitUrl: props.livekitUrl,      
    });
    props.documentBucket.grantReadWrite(backendApi.handler);

    // Only create the LiveKit agent if LiveKit is enabled
    if (props.enableLivekit) {
      const livekitAgent = new LivekitAgentEC2(this, 'LivekitAgent', {
        envName: props.envName,
        envPrefix: props.envPrefix,
        ssmParameterPath: '/bedrock-ai-assistant',
        sourceBucket: sourceBucket, // Use your existing source bucket
        instanceType: ec2.InstanceType.of(ec2.InstanceClass.T2, ec2.InstanceSize.MICRO),
        livekitApiKey: props.livekitApiKey,
        livekitApiSecret: props.livekitApiSecret,
        livekitUrl: props.livekitUrl,
      });
      
      // Add outputs for the LiveKit agent
      new CfnOutput(this, 'LivekitAgentInstanceId', {
        value: livekitAgent.instance.instanceId,
        exportName: `${props.envPrefix}${sepHyphen}LivekitAgentInstanceId`,
      });
      
      new CfnOutput(this, 'LivekitAgentPublicIp', {
        value: livekitAgent.instance.instancePublicIp,
        exportName: `${props.envPrefix}${sepHyphen}LivekitAgentPublicIp`,
      });
    }


    // Add permissions to API handler for BotStore
    botStore?.addDataAccessPolicy(
      props.envPrefix,
      "DAPolicyApiHandler",
      backendApi.handler.role!,
      ["aoss:DescribeCollectionItems"],
      ["aoss:DescribeIndex", "aoss:ReadDocument"]
    );
    
    // Add data access policy for developers
    // Get IAM user/role ARN from environment variables
    if (props.devAccessIamRoleArn) {
      // Access to BotStore
      botStore?.addDataAccessPolicy(
        props.envPrefix,
        "DAPolicyDevAccess",
        iam.Role.fromRoleArn(this, "DevAccessIamRoleArn", props.devAccessIamRoleArn),
        [
          "aoss:DescribeCollectionItems",
          "aoss:CreateCollectionItems", 
          "aoss:DeleteCollectionItems",
          "aoss:UpdateCollectionItems"
        ],
        [
          "aoss:DescribeIndex", 
          "aoss:ReadDocument", 
          "aoss:WriteDocument",
          "aoss:CreateIndex",
          "aoss:DeleteIndex",
          "aoss:UpdateIndex"
        ]
      );
    }

    // For streaming response
    const websocket = new WebSocket(this, "WebSocket", {
      accessLogBucket,
      database,
      websocketSessionTable: database.websocketSessionTable,
      auth,
      bedrockRegion: props.bedrockRegion,
      largeMessageBucket,
      documentBucket: props.documentBucket,
      enableBedrockCrossRegionInference:
        props.enableBedrockCrossRegionInference,
      enableLambdaSnapStart: props.enableLambdaSnapStart,
    });
    frontend.buildViteApp({
      backendApiEndpoint: backendApi.api.apiEndpoint,
      webSocketApiEndpoint: websocket.apiEndpoint,
      userPoolDomainPrefix: props.userPoolDomainPrefix,
      auth,
      idp,
    });

    const cloudFrontWebDistribution = frontend.cloudFrontWebDistribution.node
      .defaultChild as Distribution;
    props.documentBucket.addCorsRule({
      allowedMethods: [HttpMethods.PUT],
      allowedOrigins: [
        `https://${cloudFrontWebDistribution.distributionDomainName}`, // frontend.getOrigin() is cyclic reference
        "http://localhost:5173",
        "*",
      ],
      allowedHeaders: ["*"],
      maxAge: 3000,
    });

    const embedding = new Embedding(this, "Embedding", {
      bedrockRegion: props.bedrockRegion,
      database,
      documentBucket: props.documentBucket,
      bedrockCustomBotProject: bedrockCustomBotCodebuild.project,
      enableRagReplicas: props.enableRagReplicas,
    });

    // WebAcl for published API
    const webAclForPublishedApi = new WebAclForPublishedApi(
      this,
      "WebAclForPublishedApi",
      {
        envPrefix: props.envPrefix,
        allowedIpV4AddressRanges: props.publishedApiAllowedIpV4AddressRanges,
        allowedIpV6AddressRanges: props.publishedApiAllowedIpV6AddressRanges,
      }
    );

    new CfnOutput(this, "DocumentBucketName", {
      value: props.documentBucket.bucketName,
    });
    new CfnOutput(this, "FrontendURL", {
      value: frontend.getOrigin(),
    });

    // Outputs for API publication
    new CfnOutput(this, "PublishedApiWebAclArn", {
      value: webAclForPublishedApi.webAclArn,
      exportName: `${props.envPrefix}${sepHyphen}PublishedApiWebAclArn`,
    });
    new CfnOutput(this, "ConversationTableNameV3", {
      value: database.conversationTable.tableName,
      exportName: `${props.envPrefix}${sepHyphen}BedrockClaudeChatConversationTableName`,
    });
    new CfnOutput(this, "BotTableNameV3", {
      value: database.botTable.tableName,
      exportName: `${props.envPrefix}${sepHyphen}BedrockClaudeChatBotTableNameV3`,
    });
    new CfnOutput(this, "TableAccessRoleArn", {
      value: database.tableAccessRole.roleArn,
      exportName: `${props.envPrefix}${sepHyphen}BedrockClaudeChatTableAccessRoleArn`,
    });
    new CfnOutput(this, "LargeMessageBucketName", {
      value: largeMessageBucket.bucketName,
      exportName: `${props.envPrefix}${sepHyphen}BedrockClaudeChatLargeMessageBucketName`,
    });
  }
}
