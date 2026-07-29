from pydantic import BaseModel, ConfigDict, field_serializer

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class FollowersResponse(BaseSchema):
    mutual_user_username: str | None

class InstagramUserResponse(BaseSchema):
    insta_user_id: int
    username: str
    full_name: str | None
    profile_pic: str | None
    followers: int
    following: int
    mediacount: int
    followers_usernames: list[FollowersResponse]

    @field_serializer("followers_usernames")
    def serialize_followers(self, followers):
        return[follower.mutual_user_username for follower in followers]

class paginationRespopnse(BaseSchema):
    data: list[InstagramUserResponse]
    next_cursor : str | None
    has_next : bool