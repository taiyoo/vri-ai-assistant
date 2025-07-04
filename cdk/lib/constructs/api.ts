import { Construct } from "constructs";
import { CfnOutput, CfnResource, Duration } from "aws-cdk-lib";
import { ITable } from "aws-cdk-lib/aws-dynamodb";
import { HttpLambdaIntegration } from "aws-cdk-lib/aws-apigatewayv2-integrations";
import { HttpUserPoolAuthorizer } from "aws-cdk-lib/aws-apigatewayv2-authorizers";
import {
  Architecture,
  // Code,
  IFunction,
  LayerVersion,
  Runtime,
  SnapStartConf,
} from "aws-cdk-lib/aws-lambda";
import {
  CorsHttpMethod,
  HttpApi,
  HttpMethod,
} from "aws-cdk-lib/aws-apigatewayv2";
import { Auth } from "./auth";
import { Stack } from "aws-cdk-lib";
import * as iam from "aws-cdk-lib/aws-iam";
import * as logs from "aws-cdk-lib/aws-logs";
import * as path from "path";
import { IBucket } from "aws-cdk-lib/aws-s3";
import * as codebuild from "aws-cdk-lib/aws-codebuild";
import { UsageAnalysis } from "./usage-analysis";
import { excludeDockerImage } from "../constants/docker";
import { PythonFunction } from "@aws-cdk/aws-lambda-python-alpha";
import { Database } from "./database";
import * as ssm from 'aws-cdk-lib/aws-ssm';

export interface ApiProps {
  readonly database: Database;
  readonly envName: string;
  readonly envPrefix: string;
  readonly corsAllowOrigins?: string[];
  readonly auth: Auth;
  readonly bedrockRegion: string;
  readonly documentBucket: IBucket;
  readonly largeMessageBucket: IBucket;
  readonly apiPublishProject: codebuild.IProject;
  readonly bedrockCustomBotProject: codebuild.IProject;
  readonly usageAnalysis?: UsageAnalysis;
  readonly enableBedrockCrossRegionInference: boolean;
  readonly enableLambdaSnapStart: boolean;
  readonly openSearchEndpoint?: string;
  // Add LiveKit props
  readonly enableLivekit?: boolean;  
  readonly livekitApiKey?: string;
  readonly livekitApiSecret?: string; 
  readonly livekitUrl?: string;
}

export class Api extends Construct {
  readonly api: HttpApi;
  readonly handler: IFunction;
  constructor(scope: Construct, id: string, props: ApiProps) {
    super(scope, id);

    const { database, corsAllowOrigins: allowOrigins = ["*"] } = props;
    const { tableAccessRole } = database;

    const usageAnalysisOutputLocation =
      `s3://${props.usageAnalysis?.resultOutputBucket.bucketName}` || "";

    const handlerRole = new iam.Role(this, "HandlerRole", {
      assumedBy: new iam.ServicePrincipal("lambda.amazonaws.com"),
    });
    handlerRole.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName(
        "service-role/AWSLambdaBasicExecutionRole"
      )
    );
    handlerRole.addToPolicy(
      // Assume the table access role for row-level access control.
      new iam.PolicyStatement({
        actions: ["sts:AssumeRole"],
        resources: [tableAccessRole.roleArn],
      })
    );
    handlerRole.addToPolicy(
      new iam.PolicyStatement({
        actions: ["bedrock:*"],
        resources: ["*"],
      })
    );
    handlerRole.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ["codebuild:StartBuild"],
        resources: [
          props.apiPublishProject.projectArn,
          props.bedrockCustomBotProject.projectArn,
        ],
      })
    );
    handlerRole.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          "cloudformation:DescribeStacks",
          "cloudformation:DescribeStackEvents",
          "cloudformation:DescribeStackResource",
          "cloudformation:DescribeStackResources",
          "cloudformation:DeleteStack",
        ],
        resources: [`*`],
      })
    );
    handlerRole.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ["codebuild:BatchGetBuilds"],
        resources: [
          props.apiPublishProject.projectArn,
          props.bedrockCustomBotProject.projectArn,
        ],
      })
    );
    handlerRole.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          "apigateway:GET",
          "apigateway:POST",
          "apigateway:PUT",
          "apigateway:DELETE",
        ],
        resources: [`arn:aws:apigateway:${Stack.of(this).region}::/*`],
      })
    );
    handlerRole.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          "athena:GetWorkGroup",
          "athena:StartQueryExecution",
          "athena:StopQueryExecution",
          "athena:GetQueryExecution",
          "athena:GetQueryResults",
          "athena:GetDataCatalog",
        ],
        resources: [props.usageAnalysis?.workgroupArn || ""],
      })
    );
    handlerRole.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ["glue:GetDatabase", "glue:GetDatabases"],
        resources: [
          props.usageAnalysis?.database.databaseArn || "",
          props.usageAnalysis?.database.catalogArn || "",
        ],
      })
    );
    handlerRole.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          "glue:GetDatabase",
          "glue:GetTable",
          "glue:GetTables",
          "glue:GetPartition",
          "glue:GetPartitions",
        ],
        resources: [
          props.usageAnalysis?.database.databaseArn || "",
          props.usageAnalysis?.database.catalogArn || "",
          props.usageAnalysis?.ddbExportTable.tableArn || "",
        ],
      })
    );
    handlerRole.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          "cognito-idp:AdminGetUser",
          "cognito-idp:AdminListGroupsForUser",
          "cognito-idp:ListUsers",
          "cognito-idp:ListGroups",
        ],
        resources: [props.auth.userPool.userPoolArn],
      })
    );
    handlerRole.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: [
          "aoss:APIAccessAll",
          "aoss:DescribeCollection",
          "aoss:GetCollection",
          "aoss:SearchCollections",
          "aoss:BatchGetCollection",
          "aoss:ListCollections",
        ],
        resources: ["*"],
      })
    );
    handlerRole.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ["aoss:DescribeIndex", "aoss:ReadDocument"],
        resources: [
          `arn:aws:aoss:${Stack.of(this).region}:${
            Stack.of(this).account
          }:collection/*`,
        ],
      })
    );
    // For Firecrawl api key
    handlerRole.addToPolicy(
      new iam.PolicyStatement({
        actions: [
          "secretsmanager:CreateSecret",
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:RestoreSecret",
          "secretsmanager:PutSecretValue",
          "secretsmanager:UpdateSecretVersionStage",
          "secretsmanager:DeleteSecret",
          "secretsmanager:RotateSecret",
          "secretsmanager:CancelRotateSecret",
          "secretsmanager:UpdateSecret",
          "secretsmanager:TagResource",
        ],
        resources: [
          `arn:aws:secretsmanager:${Stack.of(this).region}:${
            Stack.of(this).account
          }:secret:firecrawl/*/*`,
        ],
      })
    );
    props.usageAnalysis?.resultOutputBucket.grantReadWrite(handlerRole);
    props.usageAnalysis?.ddbBucket.grantRead(handlerRole);
    props.largeMessageBucket.grantReadWrite(handlerRole);

    // Get parameters from SSM if LiveKit is enabled
    let livekitApiKey, livekitApiSecret, livekitUrl, liveKitPluginOpenAIAPIKey, liveKitPluginDeepgramAPIKey;
    if (props.enableLivekit) {
      try {
        livekitApiKey = ssm.StringParameter.fromSecureStringParameterAttributes(this, 'LiveKitApiKey', {
          parameterName: '/bedrock-ai-assistant/livekit/api-key',
        }).stringValue;
        
        livekitApiSecret = ssm.StringParameter.fromSecureStringParameterAttributes(this, 'LiveKitApiSecret', {
          parameterName: '/bedrock-ai-assistant/livekit/api-secret',
        }).stringValue;
        
        livekitUrl = ssm.StringParameter.fromStringParameterAttributes(this, 'LiveKitUrl', {
          parameterName: '/bedrock-ai-assistant/livekit/url',
        }).stringValue;

        liveKitPluginOpenAIAPIKey = ssm.StringParameter.fromStringParameterAttributes(this, 'LiveKitPluginOpenAIAPIKey', {
          parameterName: '/bedrock-ai-assistant/livekit/plugin/openai-api-key',
        }).stringValue;

        liveKitPluginDeepgramAPIKey = ssm.StringParameter.fromStringParameterAttributes(this, 'LiveKitPluginDeepgramAPIKey', {
          parameterName: '/bedrock-ai-assistant/livekit/plugin/deepgram-api-key',
        }).stringValue;

      } catch (error) {
        console.warn('Could not load LiveKit parameters from SSM, LiveKit will be disabled');
      }
    }

    const handler = new PythonFunction(this, "HandlerV2", {
      entry: path.join(__dirname, "../../../backend"),
      index: "app/main.py",
      bundling: {
        assetExcludes: [...excludeDockerImage],
        buildArgs: { POETRY_VERSION: "1.8.3" },
      },
      runtime: Runtime.PYTHON_3_13,
      architecture: Architecture.X86_64,
      memorySize: 1024,
      timeout: Duration.minutes(15),
      environment: {
        CONVERSATION_TABLE_NAME: database.conversationTable.tableName,
        BOT_TABLE_NAME: database.botTable.tableName,
        ENV_NAME: props.envName,
        ENV_PREFIX: props.envPrefix,
        CORS_ALLOW_ORIGINS: allowOrigins.join(","),
        USER_POOL_ID: props.auth.userPool.userPoolId,
        CLIENT_ID: props.auth.client.userPoolClientId,
        ACCOUNT: Stack.of(this).account,
        REGION: Stack.of(this).region,
        BEDROCK_REGION: props.bedrockRegion,
        TABLE_ACCESS_ROLE_ARN: tableAccessRole.roleArn,
        DOCUMENT_BUCKET: props.documentBucket.bucketName,
        LARGE_MESSAGE_BUCKET: props.largeMessageBucket.bucketName,
        PUBLISH_API_CODEBUILD_PROJECT_NAME: props.apiPublishProject.projectName,
        // KNOWLEDGE_BASE_CODEBUILD_PROJECT_NAME:
        //   props.bedrockCustomBotProject.projectName,
        USAGE_ANALYSIS_DATABASE:
          props.usageAnalysis?.database.databaseName || "",
        USAGE_ANALYSIS_TABLE:
          props.usageAnalysis?.ddbExportTable.tableName || "",
        USAGE_ANALYSIS_WORKGROUP: props.usageAnalysis?.workgroupName || "",
        USAGE_ANALYSIS_OUTPUT_LOCATION: usageAnalysisOutputLocation,
        ENABLE_BEDROCK_CROSS_REGION_INFERENCE:
          props.enableBedrockCrossRegionInference.toString(),
        OPENSEARCH_DOMAIN_ENDPOINT: props.openSearchEndpoint || "",
        AWS_LAMBDA_EXEC_WRAPPER: "/opt/bootstrap",
        PORT: "8000",
        // Add LiveKit environment variables
        ENABLE_LIVEKIT: (props.enableLivekit && livekitApiKey && livekitApiSecret) ? "true" : "false",
        ...(props.enableLivekit && livekitApiKey && {
          LIVEKIT_API_KEY: livekitApiKey,
        }),
        ...(props.enableLivekit && livekitApiSecret && {
          LIVEKIT_API_SECRET: livekitApiSecret,
        }),
        ...(props.enableLivekit && livekitUrl && {
          LIVEKIT_URL: livekitUrl,
        }),
        ...(props.enableLivekit && liveKitPluginOpenAIAPIKey && {
          OPENAI_API_KEY: liveKitPluginOpenAIAPIKey,
        }),
        ...(props.enableLivekit && liveKitPluginDeepgramAPIKey && {
          DEEPGRAM_API_KEY: liveKitPluginDeepgramAPIKey,
        }),
      },
      role: handlerRole,
      logRetention: logs.RetentionDays.THREE_MONTHS,
      snapStart: props.enableLambdaSnapStart
        ? SnapStartConf.ON_PUBLISHED_VERSIONS
        : undefined,
      layers: [
        LayerVersion.fromLayerVersionArn(
          this,
          "LwaLayer",
          // https://github.com/awslabs/aws-lambda-web-adapter?tab=readme-ov-file#lambda-functions-packaged-as-zip-package-for-aws-managed-runtimes
          `arn:aws:lambda:${
            Stack.of(this).region
          }:753240598075:layer:LambdaAdapterLayerX86:23`
        ),
      ],
    });
    // https://github.com/awslabs/aws-lambda-web-adapter/tree/main/examples/fastapi-zip
    (handler.node.defaultChild as CfnResource).addPropertyOverride(
      "Handler",
      "run.sh"
    );

    const api = new HttpApi(this, "Default", {
      description: `Main API for ${Stack.of(this).stackName}`,
      corsPreflight: {
        allowHeaders: ["*"],
        allowMethods: [
          CorsHttpMethod.GET,
          CorsHttpMethod.HEAD,
          CorsHttpMethod.OPTIONS,
          CorsHttpMethod.POST,
          CorsHttpMethod.PUT,
          CorsHttpMethod.PATCH,
          CorsHttpMethod.DELETE,
        ],
        allowOrigins: allowOrigins,
        maxAge: Duration.days(10),
      },
    });

    const integration = new HttpLambdaIntegration(
      "Integration",
      handler.currentVersion
    );
    const authorizer = new HttpUserPoolAuthorizer(
      "Authorizer",
      props.auth.userPool,
      {
        userPoolClients: [props.auth.client],
      }
    );

    // Add documentation routes without authorization
    api.addRoutes({
      path: "/docs",
      methods: [HttpMethod.GET],
      integration
    });

    api.addRoutes({
      path: "/redoc",
      methods: [HttpMethod.GET],
      integration
    });

    api.addRoutes({
      path: "/openapi.json",
      methods: [HttpMethod.GET],
      integration
    });
    
    let routeProps: any = {
      path: "/{proxy+}",
      integration,
      methods: [
        HttpMethod.GET,
        HttpMethod.POST,
        HttpMethod.PUT,
        HttpMethod.PATCH,
        HttpMethod.DELETE,
      ],
      authorizer,
    };

    api.addRoutes(routeProps);

    this.api = api;
    this.handler = handler;

    new CfnOutput(this, "BackendApiUrl", { value: api.apiEndpoint });
  }
}
