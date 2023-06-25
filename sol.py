import solara
import requests
from requests.adapters import HTTPAdapter, Retry


endpoint_url = "http://localhost:8000"
# s = requests.Session()

# retries = Retry(
#     total=3,
#     backoff_factor=0.1,
#     status_forcelist=[500, 502, 503, 504]
# )

# s.mount('http://', HTTPAdapter(max_retries=retries))


text = solara.reactive("")

@solara.component
def Page():
    solara.InputText("Enter some text", value=text)

    res = requests.post(
        f"{endpoint_url}/query",
        json={'query': text.value}
    )


    solara.Markdown(f"**You entered**: {res.json()}")
    #solara.Markdown(f"**You entered**: {text.value}")