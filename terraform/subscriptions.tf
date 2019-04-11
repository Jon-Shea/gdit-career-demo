resource "aws_sns_topic_subscription" "demo_topic_sqs_subscription" {
	count = "${var.number_of_groups}"

	topic_arn = "${aws_sns_topic.demo_topic.arn}"
	protocol  = "sqs"
	endpoint  = "${aws_sqs_queue.group_queue.*.arn[count.index]}"
}

resource "aws_sns_topic_subscription" "sns_push_to_lambda" {
	topic_arn = "${aws_sns_topic.demo_topic.arn}"
	protocol = "lambda"
	endpoint = "${aws_lambda_function.sts_to_dynamo_lambda.arn}"
}