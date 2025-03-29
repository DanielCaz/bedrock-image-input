import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import {
  aws_apigateway as apigw,
  aws_s3 as s3,
  aws_s3_notifications as s3Notifications,
  aws_stepfunctions as sfMachine,
  aws_sqs as sqs,
  aws_lambda as lambda,
  aws_lambda_event_sources as lambdaSources,
} from "aws-cdk-lib";
import { ccloud_lambda } from "@compucloud-mx/ccloud-cdk-lib";

export class BedrockImageInfrastructureStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const { lambdaPresigned } = this.buildApiGateway();

    const bucketPDF = new s3.Bucket(this, "PDFBucket", {
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      cors: [
        {
          allowedMethods: [s3.HttpMethods.POST],
          allowedOrigins: ["*"],
        },
      ],
    });

    const bucketImages = new s3.Bucket(this, "ImagesBucket", {
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    const queue = new sqs.Queue(this, "ImageQueue", {
      visibilityTimeout: cdk.Duration.minutes(1),
    });

    bucketPDF.addObjectCreatedNotification(
      new s3Notifications.SqsDestination(queue),
      {
        suffix: ".pdf",
      }
    );

    lambdaPresigned.function.addEnvironment(
      "BUCKET_NAME",
      bucketPDF.bucketName
    );

    bucketPDF.grantPut(lambdaPresigned.function);

    const startStepFunction = new ccloud_lambda.Function(
      this,
      "StartStepFunction",
      {
        codePath: "lambda/functions/start_sf",
        powertoolsLayerVersion: 7,
        timeout: cdk.Duration.minutes(1),
      }
    );

    const layerPyMuPDF = new lambda.LayerVersion(this, "PyMuPDFLayer", {
      code: lambda.Code.fromAsset("lambda/layers/PyMuPDF"),
      compatibleRuntimes: [
        lambda.Runtime.PYTHON_3_9,
        lambda.Runtime.PYTHON_3_10,
        lambda.Runtime.PYTHON_3_11,
        lambda.Runtime.PYTHON_3_12,
        lambda.Runtime.PYTHON_3_13,
      ],
      compatibleArchitectures: [lambda.Architecture.X86_64],
    });

    const lambdaExtractImages = new ccloud_lambda.Function(
      this,
      "ExtractImagesFunction",
      {
        codePath: "lambda/functions/extract_images",
        powertoolsLayerVersion: 7,
        environment: {
          BUCKET_NAME: bucketImages.bucketName,
        },
        timeout: cdk.Duration.minutes(5),
        memorySize: 1024,
        architecture: lambda.Architecture.X86_64,
        additionalLayers: [layerPyMuPDF],
      }
    );

    const lambdaCallBedrock = new ccloud_lambda.Function(
      this,
      "CallBedrockFunction",
      {
        codePath: "lambda/functions/call_bedrock",
        powertoolsLayerVersion: 7,
        timeout: cdk.Duration.minutes(5),
        memorySize: 1024,
      }
    );

    const stateMachine = new sfMachine.StateMachine(this, "ImageStateMachine", {
      definitionBody: sfMachine.DefinitionBody.fromFile(
        "stepfunctions/image-state-machine.asl.json"
      ),
      definitionSubstitutions: {
        lambdaExtractImages: lambdaExtractImages.function.functionArn,
        lambdaCallBedrock: lambdaCallBedrock.function.functionArn,
      },
      tracingEnabled: true,
    });

    startStepFunction.function.addEnvironment(
      "STATE_MACHINE_ARN",
      stateMachine.stateMachineArn
    );

    stateMachine.grantStartExecution(startStepFunction.function);
    lambdaExtractImages.function.grantInvoke(stateMachine);
    lambdaCallBedrock.function.grantInvoke(stateMachine);

    startStepFunction.function.addEventSource(
      new lambdaSources.SqsEventSource(queue)
    );

    bucketPDF.grantRead(lambdaExtractImages.function);
    bucketImages.grantPut(lambdaExtractImages.function);
    bucketImages.grantRead(lambdaCallBedrock.function);
  }

  private buildApiGateway() {
    const api = new apigw.RestApi(this, "BedrockImageApi", {
      deployOptions: {
        tracingEnabled: true,
      },
      defaultCorsPreflightOptions: {
        allowOrigins: apigw.Cors.ALL_ORIGINS,
        allowMethods: apigw.Cors.ALL_METHODS,
      },
    });

    const lambdaPresigned = new ccloud_lambda.Function(
      this,
      "PresignedUrlFunction",
      {
        codePath: "lambda/functions/presigned",
        powertoolsLayerVersion: 7,
        timeout: cdk.Duration.seconds(30),
      }
    );

    const resourcePresigned = api.root.addResource("presigned");
    resourcePresigned.addMethod(
      "POST",
      new apigw.LambdaIntegration(lambdaPresigned.function)
    );

    return { lambdaPresigned };
  }
}
