#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";
import { BedrockImageInfrastructureStack } from "../lib/bedrock-image-infrastructure-stack";

const app = new cdk.App();
new BedrockImageInfrastructureStack(app, "BedrockImageInfrastructureStack", {
  env: { account: "881746487492", region: "us-east-1" },
});
