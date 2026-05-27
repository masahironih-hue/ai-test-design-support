import * as cdk from "aws-cdk-lib";
import { CfnOutput, RemovalPolicy } from "aws-cdk-lib";
import * as apigwv2 from "aws-cdk-lib/aws-apigatewayv2";
import * as integrations from "aws-cdk-lib/aws-apigatewayv2-integrations";
import * as dynamodb from "aws-cdk-lib/aws-dynamodb";
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

    const historiesTable = new dynamodb.Table(this, "TestDesignHistoriesTable", {
      partitionKey: {
        name: "history_id",
        type: dynamodb.AttributeType.STRING,
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: RemovalPolicy.DESTROY,
    });

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

    executionRole.addToPolicy(
      new iam.PolicyStatement({
        actions: ["dynamodb:PutItem", "dynamodb:GetItem", "dynamodb:Scan"],
        resources: [historiesTable.tableArn],
      }),
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
          HISTORIES_TABLE_NAME: historiesTable.tableName,
        },
        description:
          "Mock generator and history API for ai-test-design-support",
      },
    );

    generateFunction.node.addDependency(logGroup);
    generateFunction.node.addDependency(historiesTable);

    const httpApi = new apigwv2.HttpApi(this, "BackendHttpApi", {
      apiName: `${projectName}-backend-api`,
      description:
        "HTTP API for ai-test-design-support backend mock generator and histories",
      corsPreflight: {
        allowHeaders: ["content-type"],
        allowMethods: [
          apigwv2.CorsHttpMethod.GET,
          apigwv2.CorsHttpMethod.OPTIONS,
          apigwv2.CorsHttpMethod.POST,
        ],
        allowOrigins: [allowedOrigin],
        maxAge: cdk.Duration.days(1),
      },
    });

    const generateIntegration = new integrations.HttpLambdaIntegration(
      "GenerateTestDesignIntegration",
      generateFunction,
    );

    httpApi.addRoutes({
      path: "/test-designs/generate",
      methods: [apigwv2.HttpMethod.POST],
      integration: generateIntegration,
    });

    httpApi.addRoutes({
      path: "/test-designs/histories",
      methods: [apigwv2.HttpMethod.GET],
      integration: generateIntegration,
    });

    httpApi.addRoutes({
      path: "/test-designs/histories/{history_id}",
      methods: [apigwv2.HttpMethod.GET],
      integration: generateIntegration,
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

    new CfnOutput(this, "TestDesignHistoriesPath", {
      description: "Path for the test design history list API",
      value: "/test-designs/histories",
    });
  }
}
