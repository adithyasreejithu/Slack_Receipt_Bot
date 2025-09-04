import os, pathlib, requests
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()   # This loads the env variables 
BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]   # API key for bot
CHANNEL_ID = os.environ["CHANNEL_ID"] # Channel ID 
download_loc = os.environ["DOWNLOAD_LOC"]

client = WebClient(token=BOT_TOKEN)
DOWNLOAD_DIR = pathlib.Path(download_loc)
DOWNLOAD_DIR.mkdir(exist_ok=True)
    
# Call function to map users ID to name 
def create_user_map() -> dict[str,   str]: 
    cursor = None
    user_map = {}
    while True: 
        try:
            response = client.users_list(limit=200, cursor=cursor)
            members = response.get("members",[])
            for m in members:
                user_id = m.get("id")
                profile = m.get("profile",{}) or {}
                name  = profile.get("real_name") or profile.get("display_name")
                user_map[user_id] = name

                
        except SlackApiError as e:
            print("users.list error:", e.response.get("error"))
            break

        cursor = response.get("response_metadata", {}).get("next_cursor")

        if not cursor:
            break

    return user_map
# Need to rename the file



# Create funcition to download files 
def download_files(file_url : str, save_path : str):  # url_private_download from slack files json, and path to be saved
    req = requests.get(
        file_url,
        headers={"Authorization": f"Bearer {BOT_TOKEN}"},
        timeout= 30)
    
    req.raise_for_status()
    with open(save_path, "wb") as f:
        f.write(req.content)

def channel_history(chan_id : str):
    user_map = create_user_map()
    cursor = None 
    total_msg = 0 
    files = []
    while True: 
        try: 
            response = client.conversations_history(
                channel=chan_id,
                cursor = cursor, 
                limit=200,
            )

            messages = response.get('messages',[])
            # Breaks down into individual messages 
            for m in reversed(messages): 
                files = m.get('files') or []

                if not files: 
                    continue

                upload_user = user_map.get(m["user"])
                path = DOWNLOAD_DIR/f["name"]
                download_files(url, path)
                    
        except SlackApiError as e:
            print("API error:", e.response.get("error"))
            break 

        cursor = response.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break
    
    for f in files: 
        print(
            "msg_ts:", m.get("ts"),
            "\nuser:", m.get("user"),
            "\nfile_name:", f.get("name"),
            "\nmime:", f.get("mimetype"),
        )
        user_name = user_map.get(f["user"])
        print(user_name)
        url = f.get("url_private_download")
        path = DOWNLOAD_DIR/f["name"]
        # download_files(url, path)


    all_files = []
    for m in reversed(messages):
        for f in (m.get("files") or []):
            all_files.append((m, f))

    # later
    for m, f in all_files:
        print("msg_ts:", m.get("ts"), "file:", f.get("name"))

if __name__ == "__main__":
    channel_history(CHANNEL_ID)