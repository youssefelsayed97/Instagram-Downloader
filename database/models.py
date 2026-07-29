from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, BigInteger, Boolean, Integer, Text, ForeignKey, UniqueConstraint


class Base(DeclarativeBase):
    pass


class InstagramUser(Base):
    __tablename__ = 'instagram_users'
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    insta_user_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        index=True
    )

    username: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        index=True
    )

    full_name: Mapped[str] = mapped_column(
        String(100)
    )

    is_private: Mapped[bool] = mapped_column(
        Boolean
    )

    biography: Mapped[str] = mapped_column(
        Text
    )

    followers: Mapped[int] = mapped_column(
        Integer
    )

    following: Mapped[int] = mapped_column(
        Integer
    )

    mediacount: Mapped[int] = mapped_column(
        Integer
    )

    profile_pic: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    followers_usernames: Mapped[list["MutualFollower"]] = relationship(
        back_populates="user"
    )

class MutualFollower(Base):
    __tablename__ = "mutual_followers"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "mutual_user_id",
            name="unique_mutual_follower" # constraint name in db
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    username: Mapped[str] = mapped_column(
        String(30),
        index=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("instagram_users.insta_user_id")
    )

    mutual_user_id: Mapped[int] = mapped_column(
        BigInteger
    )

    mutual_user_username: Mapped[str] = mapped_column(
        String(30)
    )

    user: Mapped[InstagramUser] = relationship(
        back_populates="followers_usernames"
    )