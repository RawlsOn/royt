from django.db import models

import user.models as user_models

from rticler.models.base_post import BasePost
from rticler.models.article import Article

class Comment(BasePost):

    article = models.ForeignKey(
        Article,
        on_delete= models.CASCADE, null= True, blank= True
    )

    user = models.ForeignKey(
        user_models.CustomUser,
        on_delete= models.CASCADE, null= True
    )
