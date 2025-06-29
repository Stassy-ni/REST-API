from marshmallow import Schema, fields

class FeedbackSchema(Schema):
    class Meta:
        ordered = True
        # Имя схемы для OpenAPI — уникальное!
        schema_name = "FeedbackSchema"

    id = fields.Int(dump_only=True)
    last_name = fields.Str(required=True)
    first_name = fields.Str(required=True)
    middle_name = fields.Str(allow_none=True)
    email = fields.Email(required=True)
    message = fields.Str(required=True, validate=lambda m: len(m.strip()) > 0)
    answer_method = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)