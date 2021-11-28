## YouTube Subscription and Playlists Merger:
The intention of this project to help switching from an old personal YouTube channel to a new one without loosing subscription to channels and personal playlists.

<br>
<br>

*First, We must do some hard and technical steps, for this script to run and has the needed permissions.*

<br>

**Note:**
<br>
In order to access private and unlisted playlists, the authentication method must be OAUTH 2.0.<br>
Normal access token allows for public playlists only.<br>

<br>

### **Enable OAuth 2.0:**

To enable OAUTH 2.0, you must have a project and OAuth 2.0 client ID.
<br>
In case you don't have one already, here is how:
1. Go to [Google Cloud console](https://console.cloud.google.com/apis/dashboard)
2. Create new project, choose whatever name you prefer.


Now, we need to add a consent screen for our app:
1. In the side menu select "OAuth consent screen"
2. choose a name, and add your google account as User support email and Developer contact information.
3. Save and continue.
4. Click on Add or remove scopes, it will open a side menu on the right.
5. Filter for "YouTube Data API v3", if you did not find it, go to this [link](https://console.cloud.google.com/apis/library/youtube.googleapis.com) and press enable.
6. Now, you can search for "youtube" and select "youtube.readonly" and "youtube"
7. Save and continue.<br>
   *Note:* In case you did not find them after enabling "YouTube Data API v3", refresh the consent webpage and search again, it should appear.
8. Add your google emails for all users, that have the channels to merge as test users.<br>
*Note:* I add my email only, because both channels were linked to the same account.
Save and continue.
Back to Dashboard.
<br>

Hurray, First hard step is done.

<br>

### **Creating credentials:**
1. In the side menu select "credentials" then "create credentials"
2. "OAuth Client ID"
3. Choose a name, in my case "YouTube channel merger"
4. For Authorized redirect URIs copy and paste "http://localhost:8080/"
   <br>*Note:* Do not forget the last back slash
5. Download OAuth Client or Download JSON
6. Rename the file to "SECRETS.json"
7. Move "SECRETS.json" to the same folder as "youtube_fetch.py"

Your "SECRETS.json" should look like this:
```
{
  "web": {
    "client_id": "****",
    "project_id": "****",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "****"
  }
}
```
<br>

*Done from Google side* :v:
<br>
<br>

### Installing Python Libraries:
```
pip install google-api-python-client
pip install google-auth-oauthlib
```
<br>


### Creating "channels_info.json":
Create a "channels_info.json" and place it beside "youtube_fetch.py" in the same folder:
```
{
    "channel_source": "channel id",
    "channel_target": "channel id"
}
```
<br>
Your JSON file must contain the ids for both channel:<br>
*channel_source:* the channel which the script will collect subscriber and playlists.<br>
*channel_target:* the channel which the script will insert playlists and subscribe to subscriber.<br><br>

**Now we are ready to start fetching data from the source channel and inserting to the target channel.**<br><br>

### **YouTube Quota:**
Please be aware, that YouTube api has a daily quota of 10,000 units at the day I wrote this script.<br>
This units will reset each day, and each request to get or update data cost differently.<br>

For my channel, I collected all my subscription and playlists in one shot.<br>
*But* creating playlists was costly, and had to do it in multiple runs.<br>
*Don't worry*, the script can pick up from last inserted video and continue till quota is reached.<br>
I had to run "youtube_insert.py" like five days in a row to finish inserting videos and creating playlists.<br><br><br>

### **Running the script:**
You can either open the script in an IDE of your choice and run, or you can do it in the console by:
- Navigating to the folder with all the scripts.
- First run `"python youtube_fetch.py"`
- Then `"python youtube_insert.py"`

The console will print out messages, for you to know what is happening.<br>
If quota is reached, just rerun `"python youtube_insert.py"`<br><br>

#### **Only First Time:**
"youtube_fetch.py" and "youtube_insert.py" will open the browser to ask permission to access your google account in order to collect credentials and save them for later.<br><br>
This step is necessary, and will allow the script to have access to the channels in order to read and insert, with the use of the project and consent we created at the beginning.<br><br>

The whole script is available for you to read and make sure, nothing harmful will happen to your channels.<br>
In my case, I ran it successfully and have my both channels merged.<br><br>

Thank you for your patience reading and using this script.