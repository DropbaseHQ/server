from server.schemas.page import PageProperties

def get_properties(req: PageProperties):
    return req["properties"]