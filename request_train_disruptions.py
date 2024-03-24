import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load .env as environment variables in runtime
load_dotenv()
NS_APP_KEY = os.getenv("NS_APP_KEY")


def request_train_disruptions() -> str:
    """
    This call uses the Reisinformatie API from the product `Ns-App`.
    This product also contains a `Disruptions API` with an equivalent endpoint.
    """
    if not NS_APP_KEY:
        raise Exception("NS app key not found in .env")

    endpoint = "https://gateway.apiportal.ns.nl/disruptions/v3"

    headers = {"Ocp-Apim-Subscription-Key": NS_APP_KEY}
    response = requests.get(endpoint, headers=headers, timeout=60)

    if response.status_code == 200:
        # Store the response text for reproduction
        out_fn = Path("data/disruptions.json")
        os.makedirs(out_fn.parents[0], exist_ok=True)
        with open(out_fn, mode="w", encoding="utf-8") as f:
            f.write(response.text)
        print("Response written to", out_fn)
    else:
        print("Request not successful so not written to disk.")

    disruptions = json.loads(response.text)
    return "\n".join(
        [
            f'{disruption["title"]} {disruption["timespans"][0]["cause"]["label"]}'
            for disruption in disruptions
            if (disruption["isActive"] and disruption["type"].lower() != "calamity")
        ]
    )


def request_disruptions_at_station(station_code: str) -> str:
    """
    NOTE each station has an official `station_code`.
        For example, "Nijmegen" is 'Nm'.
    """

    # TODO hoe leert de LLM de afkortingen van stations?

    if not NS_APP_KEY:
        raise Exception("NS app key not found in .env")

    endpoint = f"https://gateway.apiportal.ns.nl/disruptions/v3/station/{station_code}"

    headers = {"Ocp-Apim-Subscription-Key": NS_APP_KEY}
    response = requests.get(endpoint, headers=headers, timeout=60)

    if response.status_code == 200:
        # Store the response text for reproduction
        out_fn = Path(f"data/disruptions_at_{station_code}.json")
        os.makedirs(out_fn.parents[0], exist_ok=True)
        with open(out_fn, mode="w", encoding="utf-8") as f:
            f.write(response.text)
        print("Response written to", out_fn)
    else:
        print("Request not successful so not written to disk.")

    # Will return [] if there are no disruptions
    disruptions = json.loads(response.text)

    if disruptions:
        info = "\n".join(
            [
                f'{disruption["title"]} {disruption["timespans"][0]["cause"]["label"]}'
                for disruption in disruptions
                if (disruption["isActive"] and disruption["type"].lower() != "calamity")
            ]
        )
    else:
        info = f"Er zijn geen verstoringen bekend voor station {station_code}."

    return info
