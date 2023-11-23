from django.contrib.auth.models import AbstractUser
from django.db import models



# Create models for user, just save the user name from resigter
class User(AbstractUser):
    pass



# Create models for post_data, like content, user, date
class Post(models.Model):\
    # every post has an unique id which is auto generated by django model
    post_content = models.CharField(max_length=140)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    post_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Post id: {self.id}, Posted by: {self.user}, {self.post_date.strftime('Date: %d %b, %Y, Time: %H:%M:%S')}"
    


class Follow(models.Model):
    user_following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_who_is_following_others")
    user_follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_who_is_being_followed")

    def __str__(self) -> str:
        return f"{self.user_following} is following {self.user_follower}"
    


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user-liked+")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post-liked+")

    def __str__(self) -> str:
        return f"{self.user} liked {self.post}"

