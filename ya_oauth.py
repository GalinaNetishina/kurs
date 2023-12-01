import webbrowser
from urllib.parse import urlencode
APP_ID ="51800837"
base_url = "https://oauth.vk.com/authorize"
params = {
    "client_id": APP_ID,
    "redirect_uri": "https://oauth.vk.com/blank.html",
    "display": "popup",
    "scope": "status,photos",
    "response_type": "token"
}
url = f"{base_url}?{urlencode(params)}"
if __name__ == "__main__":
    webbrowser.open(url)