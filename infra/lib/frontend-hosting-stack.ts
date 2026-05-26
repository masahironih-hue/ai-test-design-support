import * as cdk from "aws-cdk-lib";
import { CfnOutput, RemovalPolicy } from "aws-cdk-lib";
import * as cloudfront from "aws-cdk-lib/aws-cloudfront";
import * as origins from "aws-cdk-lib/aws-cloudfront-origins";
import * as s3 from "aws-cdk-lib/aws-s3";
import { Construct } from "constructs";

export class FrontendHostingStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const projectName = "ai-test-design-support";

    const frontendBucket = new s3.Bucket(this, "FrontendBucket", {
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      encryption: s3.BucketEncryption.S3_MANAGED,
      enforceSSL: true,
      objectOwnership: s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,

      // 個人開発・検証用として削除しやすくする。
      // ただし、オブジェクトが残っている場合は destroy 前に手動削除が必要。
      removalPolicy: RemovalPolicy.DESTROY,

      // 初回は false 推奨。
      // true にすると自動削除用のカスタムリソース/Lambdaが増えるため、
      // Phase 2初期の「構成を小さく保つ」方針では使わない。
      autoDeleteObjects: false,
    });

    const distribution = new cloudfront.Distribution(this, "FrontendDistribution", {
      comment: `${projectName} frontend static hosting`,
      defaultRootObject: "index.html",
      priceClass: cloudfront.PriceClass.PRICE_CLASS_200,

      defaultBehavior: {
        origin: origins.S3BucketOrigin.withOriginAccessControl(frontendBucket, {
          originAccessLevels: [cloudfront.AccessLevel.READ],
        }),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        allowedMethods: cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
        cachedMethods: cloudfront.CachedMethods.CACHE_GET_HEAD_OPTIONS,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
        compress: true,
      },
    });

    cdk.Tags.of(this).add("Project", projectName);
    cdk.Tags.of(frontendBucket).add("Project", projectName);
    cdk.Tags.of(distribution).add("Project", projectName);

    new CfnOutput(this, "FrontendBucketName", {
      description: "S3 bucket name for frontend static files",
      value: frontendBucket.bucketName,
    });

    new CfnOutput(this, "CloudFrontDomainName", {
      description: "CloudFront domain name for frontend",
      value: distribution.distributionDomainName,
    });

    new CfnOutput(this, "CloudFrontDistributionId", {
      description: "CloudFront distribution ID for cache invalidation",
      value: distribution.distributionId,
    });
  }
}