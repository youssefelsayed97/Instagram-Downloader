import json
import logging
import os
import time
from instaloader import Profile, QueryReturnedBadRequestException, TooManyRequestsException
import creds
from scraper import Scraper
from utilits import cli_utilits



class Downloader:

    def __init__(self, logger: logging.Logger, loader, username=None, target=None, targets=None):
        self.logger = logger
        self.loader = loader
        self.username = username
        self.target = target
        self.targets = targets
        self.targetId = None
        self.profile: Profile | None = None
        self.own_profile: Profile | None = None
        self.profile_by_id: Profile | None = None
        self.scrape = Scraper(loader=self.loader)

    def set_target(self, target):
        self.target = target
    def set_username(self, username):
        self.username = username
    def set_targets(self, targets):
        self.targets = targets

    def set_profile(self, profile):
        self.profile = profile

    def search_for_profile(self, search_query):# logger
        result = self.scrape.search_account(search_query)
        return result

    def get_own_profile(self) -> Profile | None:
        if self.own_profile:
            return self.own_profile
        try:
            self.own_profile = Profile.own_profile(self.loader.context)
            return self.own_profile
        except Exception as e:
            self.logger.error(f"Error while graping own Profile from username: {e}")

    def get_profile(self) -> Profile | None:
        if self.profile:
            return self.profile
        try:
            self.profile = Profile.from_username(self.loader.context, self.target)
            return self.profile
        except Exception as e:
            self.logger.error(f"Error while graping Profile from username: {e}")
            self.logger.error(f"Cannot access the account or {self.target} not exist!")
            return None
            # your account needs action

    def get_profile_by_id(self, id_) -> Profile | None:
        if self.profile_by_id:
            if self.profile_by_id.userid == id_:
                return self.profile_by_id
        try:
            self.profile_by_id = Profile.from_id(self.loader.context, id_)
            return self.profile_by_id
        except:
            self.logger.error(f"id: {id_} Not exist!")

    def get_username(self, user_id) -> str:
        username = self.get_profile_by_id(user_id).username
        return username

    def mutual_usernames_graper(self) -> list[str]:
        usernames = []
        ids = self.profile.mutual_followers_ids
        try:
            for id_ in ids:
                try:
                    usernames.append(self.get_username(id_))
                except:
                    continue
            return usernames
        except:
            return []

    def get_all_mutual_followers(self) -> list[str]:
        self.logger.info("Getting all mutual followers")
        usernames_graper = self.mutual_usernames_graper()
        usernames_scraper = self.scrape.mutual_followers(user_id=self.targetId)

        final_usernames = list(dict.fromkeys(usernames_graper + usernames_scraper))

        return final_usernames
    @property
    def is_private(self):
        return self.get_profile().is_private

    @property
    def is_following(self):
        return self.get_profile().followed_by_viewer

    @property
    def has_stories(self):
        # return self.get_profile().has_public_story # checks if the user has a story that is publicly visible.
        return self.get_profile().has_viewable_story # checks if you can actually view the story (based on your access).

    @property
    def has_highlights(self):
        return self.get_profile().has_highlight_reels

    @staticmethod
    def get_key_value(profile, key, default=None):
        try:
            value = getattr(profile, key, default)
            return value
        except:
            return default

    def highlights_(self):
        if not self.is_private or self.is_following:
            highlights = self.loader.grape_highlights()
            for highlight in highlights:
                for story in highlight.get_items():
                    self.loader.download_stories(story)

    def tagged_(self):
        if not self.is_private or self.is_following:
            profile = self.get_profile()
            self.loader.dir_path(f"{self.target}/Stories")
            self.loader.download_loop(profile.get_tagged_posts(), self.target)

    def user_info(self):
        profile = self.get_profile()
        self.targetId = profile.userid
        is_private = self.get_key_value(profile, "is_private")
        try:
            new_data = {
                "username": self.target,
                "info": {
                    "logged_in_as": self.username,
                    "date": creds.TIME,
                    "userid": self.targetId,
                    "profile_pic": profile.get_profile_pic_url(),
                    "full_name": self.get_key_value(profile, "full_name"),
                    "is_private": is_private,
                    "biography": self.get_key_value(profile, "biography"),
                    "biography_mentions": self.get_key_value(profile, "biography_mentions"),
                    "biography_hashtags": self.get_key_value(profile, "biography_hashtags"),
                    "external_url": self.get_key_value(profile, "external_url"),
                    "followers": self.get_key_value(profile, "followers"),
                    "following": self.get_key_value(profile, "followees"),
                    "mediacount": self.get_key_value(profile, "mediacount"),
                    "fb_name": self.get_key_value(profile, "linked_fb_info_name"),
                    "fb_profile_url": self.get_key_value(profile, "linked_fb_info_url"),
                    "threads username": self.get_key_value(profile, 'threads_username'),
                    "bio_links": self.get_key_value(profile, "bio_links"),
                    # "mutual_followers_usernames": self.get_key_value(profile, 'mutual_followers_usernames'),
                    # "mutual_followers_usernames": self.scrape.mutual_followers(user_id=self.targetId),
                    "mutual_followers_usernames": self.get_all_mutual_followers()
                    if is_private else [],
                    "mutual_followers_ids": self.get_key_value(profile, "mutual_followers_ids")
                    if is_private else [],
                    # "mutual_usernames_graper": self.mutual_usernames_graper(),
                    "mutual_followers_count": self.get_key_value(profile, "mutual_followers_count")
                    if is_private else []
                }
            }

            folder_path = os.path.join(creds.BASE_PATH, self.target)
            os.makedirs(folder_path, exist_ok=True)
            file_path = os.path.join(folder_path, f"{self.target}.json")

            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        old_data = json.load(f)

                        if not isinstance(old_data, list):
                            old_data = [old_data]

                    except json.JSONDecodeError:
                        old_data = []
            else:
                old_data = []

            old_data.append(new_data)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(old_data, f, indent=4, ensure_ascii=False)

            self.logger.info(f"{self.target} information has been saved successfully ✅")
            # print(new_data)
            return new_data

        except Exception as e:
            self.logger.error(f"Failed to save user info: {e}")
            return None

    def dp(self):
        self.loader.dir_path(f"{self.target}/DP")
        profile = self.get_profile()
        if not profile:
            self.logger.error(f"{self.target} not found")
            return

        self.logger.info(f"Downloading {self.target} profile picture...")
        try:
            self.loader.download_dp(profile)
        except:
            self.logger.error(f"Failed downloading {self.target} profile picture.")

    def stories(self):

        if self.has_stories and not self.is_private or self.is_following:
            self.loader.dir_path(f"{self.target}/Stories")
            profile = self.get_profile()
            if not profile:
                self.logger.error(f"{self.target} not found")
                return
            self.logger.info(f"Downloading {self.target} stories...")
            try:
                self.loader.download_stories(profile)
            except Exception as e:
                print(e)
                self.logger.error(f"Failed downloading {self.target} stories.")

    def highlights(self):
        if not self.is_private or self.is_following:

            self.loader.dir_path(f"{self.target}/Highlights")
            profile = self.get_profile()
            if not profile:
                self.logger.error(f"{self.target} not found")
                return
            self.logger.info(f"Downloading {self.target} highlights...")
            try:
                self.loader.download_highlights(profile)
            except Exception as e:
                print(e)
                self.logger.error(f"Failed downloading {self.target} highlights.")

    def posts(self):

        if not self.is_private or self.is_following: ## error condition need to check it

            self.loader.dir_path(f"{self.target}/Posts")
            profile = self.get_profile()
            if not profile:
                self.logger.error(f"{self.target} not found")
                return
            self.logger.info(f"Downloading {self.target} posts...")
            try:
                self.loader.download_posts(self.target)
            except Exception as e:
                print(e)
                self.logger.error(f"Failed downloading {self.target} posts.")

    def reels(self):
        import traceback
        if not self.is_private or self.is_following:

            self.loader.dir_path(f"{self.target}/Reels")
            profile = self.get_profile()
            if not profile:
                self.logger.error(f"{self.target} not found")
                return
            self.logger.info(f"Downloading {self.target} reels...")
            try:
                self.loader.download_reels(profile)
            except Exception as e:
                print(e)
                print(traceback.print_exc())
                self.logger.error(f"Failed downloading {self.target} reels.")

    def tagged(self):

        if not self.is_private or self.is_following:

            self.loader.dir_path(f"{self.target}/Tagged")
            profile = self.get_profile()
            if not profile:
                self.logger.error(f"{self.target} not found")
                return
            self.logger.info(f"Downloading {self.target} tagged...")
            try:
                self.loader.download_tagged(profile)
            except Exception as e:
                print(e)
                self.logger.error(f"Failed downloading {self.target} tagged.")

    def saved_posts(self):
        """
        downloads all saved posts in one folder called loggedInUsername/saved posts
        :return:
        """
        self.loader.dir_path(f"{self.username}/Saved Posts")
        self.logger.info(f"Downloading {self.username} saved posts...")
        try:
            self.loader.download_saved_posts()
        except Exception as e:
            print(e)
            self.logger.error(f"Failed downloading {self.username} saved posts.")

    def saved_posts_in_owner_folder(self):
        """
        create a folder with post owner username if not exist and download the post in the created folder
        :return:
        """
        savedPosts = self.get_own_profile()

        for i, post in enumerate(list(savedPosts.get_saved_posts()), start=1):
            self.loader.dir_path(f"{post.owner_username}")
            print(f"[ {i}]", end=" ")
            self.loader.download_post(post, post.owner_username)

    def download_all_user_highlights(self):
        self.loader.dir_path(f"{self.target}/Highlights")

        if not self.is_private or self.is_following:
            print('Checking Highlights')
            highlights_counter = len(list(self.loader.grape_highlights(self.profile)))

            if highlights_counter > 0:
                error_while_downloading_highlights = []
                self.logger.info(f'All collected highlights are = {highlights_counter}')
            else:
                self.logger.info('No highlights found.')
                return

            highlight_counter = 1
            for highlight in self.loader.grape_highlights(self.profile):
                self.logger.info(f"highlight = https://www.instagram.com/stories/highlights/{highlight.unique_id}/")

                error_highlight = False
                retry = 1
                stories_counter = None

                self.logger.info(f'[{highlight_counter}/{highlights_counter}] - [{highlight.title}]')

                while retry < 4:
                    try:
                        stories_counter = len(list(highlight.get_items()))
                        self.logger.info(f'Highlight [{highlight_counter}/{highlights_counter}] - [{highlight.title}] '
                                         f'contain [{stories_counter}] story')
                        break
                    except Exception as e:
                        self.logger.error(f'{e} \nretrying... {retry}')
                        time.sleep(5)
                        retry += 1
                        if retry == 3:
                            error_highlight = True

                if error_highlight:
                    error_while_downloading_highlights.append(f'Highlight [{highlight_counter}/{highlights_counter} -'
                                                              f' {highlight.title}]')
                    self.logger.error(f'Something went wrong while trying to download highlight number'
                                      f' {highlight_counter}')
                    highlight_counter += 1
                    continue

                story_counter = 1
                for story in highlight.get_items():
                    retries = 1
                    while retries < 4:
                        try:
                            self.logger.info(f'Downloading [{story_counter}/{stories_counter}]')
                            self.loader.download_storyitem(story, '{}'.format(self.target))
                            story_counter += 1
                            break

                        except QueryReturnedBadRequestException as e:
                            self.logger.error('QueryReturnedBadRequestException: ', {e})
                            self.logger.info("retrying after 1 min.")
                            time.sleep(60)
                            retries += 1

                        except TooManyRequestsException as e:
                            self.logger.error('TooManyRequestsException: ', {e})
                            self.logger.info("retrying after 1 min.")
                            time.sleep(60)
                            retries += 1

                        except:
                            self.logger.error(f'Error while downloading in {highlight.title} '
                                              f'[{highlight_counter}/{highlights_counter}]'
                                              f' story [{story_counter}/{stories_counter}]')

                            error_download = f'{highlight.title} [{highlight_counter}/{highlights_counter}]' \
                                             f' Story [{story_counter}/{stories_counter}]' \
                                             f'https://www.instagram.com/stories/highlights/{highlight.unique_id}'
                            error_while_downloading_highlights.append(error_download)
                            story_counter += 1
                            break

                if highlight_counter != highlights_counter:
                    highlight_counter += 1
                    time.sleep(5)

            if error_while_downloading_highlights:
                self.logger.info("Stories that are not downloaded: ")
                for err in error_while_downloading_highlights:
                    self.logger.info(f'- {err}')

    def save_to_history(self):

        cli_utilits.create_file(creds.HISTORY_DOWNLOADS)

        with open(creds.HISTORY_DOWNLOADS, 'r') as file:
            lines = file.readlines()

        id_found = False
        user_found = False
        i = 0
        for i, line in enumerate(lines):

            if self.target in line and str(self.targetId) in line:
                lines[i] = f'{creds.TIME} : {self.target} - {self.targetId}\n'
                user_found = True
                id_found = True
                self.logger.info(f"{self.target} was found in {creds.HISTORY_DOWNLOADS},"
                                 f" Time has been updated to {creds.TIME}")
                break
            if self.target not in line and str(self.targetId) in line:
                id_found = True
                user_found = False
                old_target_user = lines[i].split()[3]
                self.logger.info(f"ID: {self.targetId} was found with different username -> {old_target_user}")
                self.logger.info(f"Username: {old_target_user} -> {self.target}")
                lines[i] = f'{creds.TIME} : {self.target} - {self.targetId}\n'
                break

        if user_found and id_found:
            updated_line = lines.pop(i)
            lines.append(updated_line)

        if not user_found and not id_found:
            lines.append(f'{creds.TIME} : {self.target} - {self.profile.userid}\n')
            self.logger.info(f'Adding {self.target} To {creds.HISTORY_DOWNLOADS}')

        with open(creds.HISTORY_DOWNLOADS, 'w') as file:
            file.writelines(lines)

        self.logger.info(f'{self.target} has been added successfully.')

    def all_content(self):
        self.user_info()
        self.dp()
        self.stories()
        try:
            self.highlights()
        except:
            self.download_all_user_highlights()
        self.posts()
        self.reels()
        self.tagged()
        self.save_to_history()
        print(f"https://www.instagram.com/{self.target}")

    def group(self):
        error_users = []
        for target in self.targets:
            self.target = target
            self.profile = None
            try:
                self.all_content()
            except:
                error_users.append(target)
                continue

        return error_users



    # def download_by_link(self):
    #     loader.download_post()

    def tagged_profile(self):
        return

