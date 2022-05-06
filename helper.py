def get_content_type(response):
    content_type = response.headers.get("content-type")
    if content_type:
        return content_type.split(';')[0]