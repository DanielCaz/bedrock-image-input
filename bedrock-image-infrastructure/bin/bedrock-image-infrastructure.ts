#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";
import { BedrockImageInfrastructureStack } from "../lib/bedrock-image-infrastructure-stack";

const app = new cdk.App();
new BedrockImageInfrastructureStack(app, "BedrockImageInfrastructureStack", {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});
