from marshmallow import Schema, fields

class PlainItemSchema(Schema):
    id = fields.Integer(dump_only=True) # send on create only (not used on validation)
    name = fields.String(required=True)
    price = fields.Float(required=True)

class PlainStoreSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)


class PlainTagSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)


class ItemUpdateSchema(Schema):
    name = fields.Integer()
    price = fields.Float()


class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True, load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)


class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(ItemSchema()), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)


class TagSchema(PlainTagSchema):
    store_id = fields.Int(load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)


class TagAndItemsSchema(Schema):
    message = fields.Str()
    item = fields.Nested(ItemSchema())
    tags = fields.Nested(TagSchema())


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class UserRegisterSchema(UserSchema):
    email = fields.Str(required=True)


class TokenSchema(Schema):
    token = fields.Str(dump_only=True)