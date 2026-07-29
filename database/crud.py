from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from database.models import InstagramUser, MutualFollower
from typing import Optional

def is_profile_exist(db, instagram_user_id):
    return get_user_info(db, instagram_user_id) is not None

def create_insta_profile(db: Session, user_data: dict):
    try:
        # user_info = InstagramUser(**user_data)
        # print(user_data)
        info = user_data.get('info', {})
        user_info = InstagramUser(
            username = user_data.get('username'),
            insta_user_id = info.get('userid'),
            full_name = info.get('full_name'),
            is_private = info.get('is_private'),
            biography = info.get('biography'),
            followers = info.get('followers'),
            following = info.get('following'),
            mediacount = info.get('mediacount'),
            profile_pic = info.get('profile_pic')
        )

        if is_profile_exist(db, instagram_user_id=user_info.insta_user_id):
            update_user_info(db, instagram_user_id=user_info.insta_user_id, user_data=info)


        else:
            db.add(user_info)
            # db.flush() # Sends INSERT without committing (useful if generated IDs are needed)

        for m_user, m_id in zip(info.get('mutual_followers_usernames', []),
                                info.get('mutual_followers_ids', [])):

            mutual_exists = db.scalar(select(MutualFollower).where(
                MutualFollower.user_id == user_info.insta_user_id,
                            MutualFollower.mutual_user_id == int(m_id)
                            ))


            if not mutual_exists:

                mutual_follower =  MutualFollower(username = user_data.get("username"),
                                                  user_id=int(user_info.insta_user_id),
                                                  mutual_user_id=int(m_id),
                                                  mutual_user_username=m_user)
                db.add(mutual_follower)

        db.commit()
        return True


    except Exception as e:
        db.rollback()
        print(e)
        return False


def get_user_info(db: Session, instagram_user_id: Optional[int] = None, instagram_username: Optional[str] = None):

    if instagram_user_id is not None:
        return db.scalar(select(InstagramUser).options(selectinload(InstagramUser.followers_usernames)).where(InstagramUser.insta_user_id == instagram_user_id))
    elif instagram_username is not None:
        return db.scalar(select(InstagramUser).options(selectinload(InstagramUser.followers_usernames)).where(InstagramUser.username == instagram_username))
    else:
        return None

def get_all_users(db: Session, limit=10, cursor: int | None = None):

    query = (select(InstagramUser).options(selectinload(InstagramUser.followers_usernames)).order_by(InstagramUser.id))

    if cursor is not None:
        query = query.where(InstagramUser.id > cursor)

    users = db.scalars(query.limit(limit+1)).all()

    has_next = len(users) > limit

    if has_next:
        users = users[:limit]

    return users, has_next

def update_user_info(db: Session, instagram_user_id: int, user_data: dict):
    user_info = db.scalar(select(InstagramUser).where(InstagramUser.insta_user_id == instagram_user_id))

    if not user_info:
        return None

    for key, value in user_data.items(): #check dict data
        if hasattr(user_info, key): #  and key != "id"
            setattr(user_info, key, value)

    # db.commit()
    # db.refresh(user_info)
    return user_info


def delete_user_info(db: Session, instagram_user_id: int):
    user_info = db.scalar(select(InstagramUser).where(InstagramUser.insta_user_id == instagram_user_id))

    if not user_info:
        return False

    db.delete(user_info)
    db.commit()

    return True