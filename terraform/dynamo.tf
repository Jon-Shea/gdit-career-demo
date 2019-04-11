resource "aws_dynamodb_table" "message_log_table" {
    name = "MessageLogTable"
    read_capacity = 5
    write_capacity = 5
    hash_key = "message_digest"
    range_key = "group_id"

    attribute {
        name = "message_digest"
        type = "N"
    }

    attribute {
        name = "group_id"
        type = "N"
    }

    tags = {
        Name = "MessageLogTable"
    }
}