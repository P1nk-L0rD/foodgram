from django.db import models


class VideoProduct(models.BaseModel):
    ...
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=False, auto_now=True)
