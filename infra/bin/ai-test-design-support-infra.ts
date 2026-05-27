#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";
import { BackendApiStack } from "../lib/backend-api-stack";
import { FrontendHostingStack } from "../lib/frontend-hosting-stack";

const app = new cdk.App();

new FrontendHostingStack(app, "AiTestDesignSupportFrontendStack", {
  description: "Frontend static hosting stack for ai-test-design-support",
});

new BackendApiStack(app, "AiTestDesignSupportBackendApiStack", {
  description: "Minimal backend API stack for ai-test-design-support",
});
