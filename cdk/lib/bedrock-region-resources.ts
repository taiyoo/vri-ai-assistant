import { CfnOutput, RemovalPolicy, Stack, StackProps , Tags} from "aws-cdk-lib";
import { Construct } from "constructs";
import {
  BlockPublicAccess,
  Bucket,
  BucketEncryption,
  ObjectOwnership,
} from "aws-cdk-lib/aws-s3";


interface BedrockRegionResourcesStackProps extends StackProps {
}

export class BedrockRegionResourcesStack extends Stack {
  readonly documentBucket: Bucket

  constructor(
    scope: Construct,
    id: string,
    props: BedrockRegionResourcesStackProps
  ) {
    super(scope, id, props);

    // Add cost tracking tags
    Tags.of(this).add('AppManagerCFNStackKey', 'BedrockRegionResources');

    const prefix = Stack.of(this).region

    const accessLogBucket = new Bucket(this, `${prefix}AccessLogBucket`, {
      encryption: BucketEncryption.S3_MANAGED,
      blockPublicAccess: BlockPublicAccess.BLOCK_ALL,
      enforceSSL: true,
      removalPolicy: RemovalPolicy.DESTROY,
      objectOwnership: ObjectOwnership.OBJECT_WRITER,
      autoDeleteObjects: true,
    });

    this.documentBucket = new Bucket(this, `${prefix}DocumentBucket`, {
      encryption: BucketEncryption.S3_MANAGED,
      blockPublicAccess: BlockPublicAccess.BLOCK_ALL,
      enforceSSL: true,
      removalPolicy: RemovalPolicy.DESTROY,
      objectOwnership: ObjectOwnership.OBJECT_WRITER,
      autoDeleteObjects: true,
      serverAccessLogsBucket: accessLogBucket,
      serverAccessLogsPrefix: "DocumentBucket",
    });

    new CfnOutput(this, "DocumentBucketName", {
      value: this.documentBucket.bucketName,
    });

  } 
}
