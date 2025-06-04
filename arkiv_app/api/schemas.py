from marshmallow import Schema, fields


class LibrarySchema(Schema):
    id = fields.Int()
    name = fields.Str()
    description = fields.Str()
