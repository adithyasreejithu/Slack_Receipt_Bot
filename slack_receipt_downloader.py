import os, pathlib, requests, json
import pandas as pd 
from datetime import datetime
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
def create_user_map() -> dict[str, str]: 
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

def tracking_generator(prefix="R"):
    counter = 0
    def tracking_number():
        nonlocal counter
        counter += 1 
        return f"{prefix}{counter:03d}"
    return tracking_number

# Need to rename the file
def change_file_name(file_path: pathlib.Path, directory: pathlib.Path, make_invoice): 
    directory.mkdir(parents=True, exist_ok=True)
    while True: 
        receipt_number = make_invoice()
        file = directory/f"{receipt_number}{file_path.suffix}"

        if not file.exists():
            break

    file_path.rename(file)
    return receipt_number, file

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
    try: 
        with open(".last_ts.json") as f : 
            last_ts  = json.load(f)["last_ts"]
    except FileNotFoundError:
        last_ts = 0


    user_map = create_user_map()
    cursor = None 
    all_files = []
    rows = []

    column  =  ["Download_Date", "Purchase_Name", "Description", "Supplier", "Cost", "Message", "Purchaser","Receipt_Number", "Reimbursed"]
    receipt_info = pd.DataFrame(columns=column)
    # receipt_info["Reimbursed"] = receipt_info["Reimbursed"].fillna("No")


    make_invoice = tracking_generator("R")


    defaults = {
        "Download_Date" : "Bot_Holder", 
        "Purchase_Name": "REPLACE", 
        "Description": "REPLACE", 
        "Supplier": "Bot_Holder", 
        "Cost": "Bot_Holder", 
        "Message": "Bot_Holder", 
        "Purchaser": "Bot_Holder",
        "Receipt_Number": "Bot_Holder", 
        "Reimbursed": 'No' 
    }


    while True: 
        try: 
            response = client.conversations_history(
                channel=chan_id,
                oldest= last_ts,
                cursor = cursor, 
                limit=200,
            )

            messages = response.get('messages',[])
            # Breaks down into individual messages 
            for m in reversed(messages): 
                for f in (m.get("files") or []):
                    all_files.append((m, f))
               
                    
        except SlackApiError as e:
            print("API error:", e.response.get("error"))
            break 

        cursor = response.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break
    
    for m,f in all_files: 
        # ["Download_Date", "Purchase_Name", "Description", "Supplier", "Cost", "Message", "Purchaser","Receipt_Number", "Reimbursed"]
        user_name = user_map.get(f["user"])
        file_name = f["name"]
        newest_ts = m.get("ts")
        

        url = f.get("url_private_download")       
        downloaded_path = DOWNLOAD_DIR / file_name
        download_files(url, downloaded_path)

        invoice_num, new_path = change_file_name(downloaded_path, DOWNLOAD_DIR, make_invoice)

        info = {
            "Download_Date": datetime.fromtimestamp(float(m.get("ts"))).strftime("%Y-%m-%d"),
            "Message": m.get("text"),
            "Purchaser": user_name ,
            "Receipt_Number": invoice_num,
            "Reimbursed": "False"
        }

        row = {**defaults, **info}

        rows.append(row)

        with open(".last_ts.json", "w") as f:
            json.dump({"last_ts": newest_ts},f)

        print(info)
        
    # rows will be the access point to the dataframe     
    print(rows)

if __name__ == "__main__":
    channel_history(CHANNEL_ID)