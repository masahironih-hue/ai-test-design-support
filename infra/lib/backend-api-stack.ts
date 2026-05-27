import * as cdk from "aws-cdk-lib";
import { CfnOutput, RemovalPolicy } from "aws-cdk-lib";
import * as apigwv2 from "aws-cdk-lib/aws-apigatewayv2";
import * as integrations from "aws-cdk-lib/aws-apigatewayv2-integrations";
import * as iam from "aws-cdk-lib/aws-iam";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as logs from "aws-cdk-lib/aws-logs";
import { Construct } from "constructs";

export class BackendApiStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const projectName = "ai-test-design-support";
    const allowedOriginContext = this.node.tryGetContext("allowedOrigin");
    const allowedOrigin =
      typeof allowedOriginContext === "string" &&
      allowedOriginContext.trim().length > 0
        ? allowedOriginContext.trim()
        : "*";
    const functionName = `${projectName}-generate-test-design`;

    const logGroup = new logs.LogGroup(this, "GenerateTestDesignLogGroup", {
      logGroupName: `/aws/lambda/${functionName}`,
      retention: logs.RetentionDays.ONE_WEEK,
      removalPolicy: RemovalPolicy.DESTROY,
    });

    const executionRole = new iam.Role(this, "GenerateTestDesignRole", {
      assumedBy: new iam.ServicePrincipal("lambda.amazonaws.com"),
      description:
        "Execution role for ai-test-design-support generate test design Lambda",
    });

    executionRole.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName(
        "service-role/AWSLambdaBasicExecutionRole",
      ),
    );

    const generateFunction = new lambda.Function(
      this,
      "GenerateTestDesignFunction",
      {
        functionName,
        runtime: lambda.Runtime.PYTHON_3_12,
        handler: "handler.lambda_handler",
        code: lambda.Code.fromAsset("lambda/generate-test-design"),
        memorySize: 128,
        timeout: cdk.Duration.seconds(5),
        role: executionRole,
        environment: {
          ALLOWED_ORIGIN: allowedOrigin,
        },
        description:
          "Mock generator for POST /test-designs/generate in ai-test-design-support",
      },
    );

    generateFunction.node.addDependency(logGroup);

    const httpApi = new apigwv2.HttpApi(this, "BackendHttpApi", {
      apiName: `${projectName}-backend-api`,
      description:
        "Minimal HTTP API for ai-test-design-support backend mock generator",
      corsPreflight: {
        allowHeaders: ["content-type"],
        allowMethods: [
          apigwv2.CorsHttpMethod.OPTIONS,
          apigwv2.CorsHttpMethod.POST,
        ],
        allowOrigins: [allowedOrigin],
        maxAge: cdk.Duration.days(1),
      },
    });

    httpApi.addRoutes({
      path: "/test-designs/generate",
      methods: [apigwv2.HttpMethod.POST],
      integration: new integrations.HttpLambdaIntegration(
        "GenerateTestDesignIntegration",
        generateFunction,
      ),
    });

    cdk.Tags.of(this).add("Project", projectName);

    new CfnOutput(this, "BackendApiEndpoint", {
      description: "HTTP API endpoint for backend",
      value: httpApi.apiEndpoint,
    });

    new CfnOutput(this, "GenerateTestDesignPath", {
      description: "Path for the mock test design generation API",
      value: "/test-designs/generate",
    });
  }
}
