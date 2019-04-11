resource "aws_sqs_queue" "group_queue" {
	count = "${var.number_of_groups}"

	name = "demo-queue-${count.index}"
}

resource "aws_sqs_queue_policy" "test" {
	count = "${var.number_of_groups}"
	queue_url = "${aws_sqs_queue.group_queue.*.id[count.index]}"

	policy = <<POLICY
{
  "Version": "2012-10-17",
  "Id": "sqspolicy",
  "Statement": [
    {
      "Sid": "First",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "sqs:SendMessage",
      "Resource": "${aws_sqs_queue.group_queue.*.arn[count.index]}",
      "Condition": {
        "ArnEquals": {
          "aws:SourceArn": "${aws_sns_topic.demo_topic.arn}"
        }
      }
    }
  ]
}
POLICY
}