resource "aws_iam_role" "lambda_dynamo_role" {
  name = "lambda_dynamo_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda_role_attach" {
  role       = "${aws_iam_role.lambda_dynamo_role.name}"
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

resource "aws_iam_role_policy_attachment" "lambda_role_attach2" {
  role       = "${aws_iam_role.lambda_dynamo_role.name}"
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

data "archive_file" "lambda" {
  type = "zip"
  source_file = "${path.module}/../logger/lambda_logger.py"
  output_path = "${path.module}/../logger/lambda_logger.zip"
}

resource "aws_lambda_function" "sts_to_dynamo_lambda" {
  filename         = "${path.module}/../logger/lambda_logger.zip"
  function_name    = "sts-to-dynamo-lambda"
  role             = "${aws_iam_role.lambda_dynamo_role.arn}"

  source_code_hash = "${data.archive_file.lambda.output_base64sha256}"
  runtime          = "python3.7"
  handler = "lambda_logger.lambda_handler"

  depends_on = ["data.archive_file.lambda"]

}

resource "aws_lambda_permission" "with_sns" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.sts_to_dynamo_lambda.arn}"
  principal     = "sns.amazonaws.com"
  source_arn    = "${aws_sns_topic.demo_topic.arn}"
}