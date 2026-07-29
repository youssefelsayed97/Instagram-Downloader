import time
from utilits import cli_utilits
import commands_sys
import creds
from auth import Login
from loader import Loader
import logger_config
from downloader import Downloader
from database.db import Session_local
from database.crud import create_insta_profile, get_user_info
# import packages
# print(packages.__file__)
# print(packages.__version__)

user = ''
logger = logger_config.setup_logger()
cli = commands_sys.CommandSystem(logger)
session = Session_local()
loader = Loader()
db = Session_local()
downloader = Downloader(logger, loader)


@cli.register("help")
def help_cmd(_):
    print(f"""
                COMMANDS                DESCRIPTIONS

                @                       Indicates you are not logged in.
                
                LOGIN                   Log in to your Instagram account if the session is not valid.
                
                LSM                     Load an existing authenticated Instagram session (cookies).
                                        Use this if LOGIN fails due to checkpoint, 2FA,
                                        or other Instagram security restrictions.
                
                SEARCH [username]|[ID]  Search specific username or id in database
                
                ISEARCH [username]      Search instagram
                
                SHOW LOGS               Shows your logs.
                
                SHOW HISTORY            Show all previously [all content] downloaded users along with their IDs.
                
                DOWNLOAD [Username]     Download specific target content (stories, posts, reels, etc.) [Login required].
                
                DOWNLOAD GROUP          Downloads multiple user profiles sequentially [Login required].
                
                EXIT                    Close the program.
                
            """)

@cli.register("login")
def login_cmd(_):
    global user
    if user == "":
        logger.info("Logging in...")
        Login(loader, logger, creds.USERNAME).login(creds.PASSWORD)
        user = loader.logged_in_as()
        if user is None:
            user = ""
    else:
        print("already logged in as " + user)

@cli.register("lsm")
def load_session_manually_cmd(_):
    global user

    if user == "":
        user = loader.load_session_manually()# after command get cookies
        if user is None:
            logger.info("Failed to load session manually.")
            user = ""
        else:
            logger.info(f"Logged in as {user}")

    else:
        print("already logged in as " + user)

@cli.register("search")
def search_cmd(args):
    if args == "":
        print("username or id is required!")
    else:
        target = args[0] if args else ""
        if not target.isdigit():
            logger.info(f"Searching {target} in databsae.")
            result = get_user_info(db, instagram_username=target)
            if result is not None:
                for key, value in result.__dict__.items():
                    if not key.startswith("_"):
                        print(f"{key}: {value}")
            else:
                print(f"{target} not found.")
        else:
            logger.info(f"Searching {target} in databsae.")
            result = get_user_info(db, instagram_user_id=target)
            if result is not None:
                for key, value in result.__dict__.items():
                    if not key.startswith("_"):
                        print(f"{key}: {value}")
            else:
                print(f"{target} not found.")

@cli.register("show logs")
def show_logs_cmd(_):
    logger.info("Showing logs...")
    cli_utilits.show_logs()

@cli.register("show history")
def show_history_cmd(_):
    logger.info("Showing History Downloads...")
    cli_utilits.show_history()

@cli.register("download group")
def download_group_cmd(_):
    print("type 0 to exit.")
    group = []
    target = ''
    while target != '0':
        target = input("Target: ")
        if target != '0':
            group.append(target)

    logger.info(f"Checking usernames availability")
    availability = []
    for acc in group:
        downloader.set_target(acc)
        if downloader.get_profile() is None:
            logger.info(f"{acc} is not found.")
        else:
            logger.info(f"adding {acc} to downloader group")
            availability.append(acc)
            downloader.set_profile(None)
    group = availability

    logger.info(f"Downloading group {group}")
    downloader.set_username(user)
    downloader.set_targets(group)
    error_users = downloader.group()
    logger.info(f"downloaded group are: {group}")
    if error_users:
        logger.error(f"Error in downloading: {error_users}")

@cli.register(f"download")
def download_cmd(args):

    if user == '':
        print("Login required!")
        return
    if args == []:
        print("Target username required!")
    else:
        target = args[0] if args else ""
        if target == "":
            cli.execute(cmd=help_cmd)

        downloader.set_username(user)
        downloader.set_target(target)

        print(f"""
                    0- back
                    1- download {target} information (bio, following count, followers count, etc.).
                    2- download {target} profile picture.
                    3- download {target} stories.
                    4- download {target} highlights.
                    5- download {target} posts.
                    6- download {target} reels.
                    7- download {target} tagged posts and reels.
                    8- download all {target} content.
            """)

        choice = -1
        while True:

            try:
                choice = int(input(f"@{user}/{target}> "))
            except ValueError:
                print('Invalid input')
            if choice == 0:
                break
            elif choice == 1:
                data = downloader.user_info()
                if data:
                    added = create_insta_profile(db, data)
                    if added:
                        logger.info(f"{target}, has been added successfully in database.")
                    else:
                        logger.error("Error creating insta profile in database.")
                else:
                    logger.error("No data to creating insta profile in database.")
            elif choice == 2:
                downloader.dp()
            elif choice == 3:
                downloader.stories()

            elif choice == 4:
                try:
                    downloader.download_all_user_highlights()
                except:
                    downloader.highlights()
            elif choice == 5:
                downloader.posts()
            elif choice == 6:
                downloader.reels()
            elif choice == 7:
                downloader.tagged()
                # download.tagged_()
            elif choice == 8:
                downloader.all_content()
                return

@cli.register("download saved posts")
def download_all_cmd():
    pass

@cli.register("exit")
def exit_cmd(_):
    print("Goodbye!")
    time.sleep(3)
    exit(0)

@cli.register("isearch")
def insta_search_cmd(args):
    if user == '':
        print("Login required!")
        return

    target = args[0:] if args else ""

    downloader.set_username(user)
    downloader.search_for_profile(search_query=" ".join(target))


while True:
    cmd = input(f"@{user}>")
    cli.execute(cmd)
