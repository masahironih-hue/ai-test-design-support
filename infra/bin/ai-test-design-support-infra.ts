#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";
import { FrontendHostingStack } from "../lib/frontend-hosting-stack";

const app = new cdk.App();

new FrontendHostingStack(app, "AiTestDesignSupportFrontendStack", {
  description: "Frontend static hosting stack for ai-test-design-support",
});
