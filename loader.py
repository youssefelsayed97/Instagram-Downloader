from instaloader import Instaloader
import creds
from dotenv import load_dotenv
import os


class Loader:

    def __init__(self):
        self.l: Instaloader = Instaloader()

    def dir_path(self, download_path):
        self.l.dirname_pattern = f"{creds.BASE_PATH}/{download_path}"

    @property
    def context(self):
        return self.l.context

    def login(self, username, password):
        return self.l.login(username, password)

    def logged_in_as(self):
        return self.l.test_login()

    @property
    def is_logged_in(self):
        return self.l.context.is_logged_in

    def load_session(self, username, file):
        return self.l.load_session_from_file(username=username, filename=file)

    def load_session_manually(self):
        load_dotenv()

        self.l.load_session("", {
            "csrftoken": os.getenv("csrftoken"),
            "sessionid": os.getenv("sessionid"),
            "ds_user_id": os.getenv("ds_user_id"),
            "mid": os.getenv("mid"),
            "ig_did": os.getenv("ig_did"),
            })

        username = self.l.test_login()

        if username:
            self.l.context.username = username
            return username

        return None

    def save_session(self, path):
        return self.l.save_session_to_file(path)

    def download_dp(self, profile):
        self.l.download_profilepic(profile, )

    def download_stories(self, profile):
        self.l.download_stories(userids=[profile], fast_update=False)

    def download_highlights(self, profile):
        self.l.download_highlights(profile, fast_update=False)

    def grape_highlights(self, profile):
        return self.l.get_highlights(profile)

    def grape_tagged_posts(self, profile):
        # return profile.
        pass

    def download_loop(self, tagged_posts, target):
        return self.l.posts_download_loop(posts=tagged_posts, target=target) # test = monicamattaaa

    def download_storyitem(self, item, target):
        return self.l.download_storyitem(item, target)

    def download_posts(self, profile):
        self.l.download_profile(profile, profile_pic_only=False, profile_pic=False, fast_update=False)

    def download_reels(self, profile):
        self.l.download_reels(profile, fast_update=False)

    def download_tagged(self, profile):
        self.l.download_tagged(profile, fast_update=False)

    def download_saved_posts(self):
        self.l.download_saved_posts(fast_update=False)

    def download_post(self, post, target_folder):
        self.l.download_post(post, target=target_folder)
