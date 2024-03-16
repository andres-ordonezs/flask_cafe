import os
import requests

API_KEY = os.environ.get("MAPQUEST_API_KEY")


def get_map_url(address, city, state):
    """Get MapQuest URL for a static map for this location."""

    base = f"https://www.mapquestapi.com/staticmap/v5/map?key={API_KEY}"
    where = f"{address},{city},{state}"
    return f"{base}&center={where}&size=@2x&zoom=15&locations={where}"


def save_map(id, address, city, state):
    """Get static map and save in static/maps directory of this app."""

    # FIXME: get URL for map, download it, and save it with a path -> DONE
    #   like "PATH/static/maps/1.jpg"

    # path = os.path.abspath(os.path.dirname(__file__))

    path = os.path.abspath(os.path.dirname(__file__))

    url_address = '+'.join(address.split())
    url_city = '+'.join(city.split())
    url_state = '+'.join(state.split())

    url = get_map_url(url_address, url_city, url_state)

    response = requests.get(url)

    map_url = f"{path}/static/maps/{id}.jpg"

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Save the processed data to a file
        with open(map_url, 'wb') as file:
            for chunk in response.iter_content(chunk_size=128):
                file.write(chunk)
        print('Data saved successfully.')

        return f"/static/maps/{id}.jpg"

    else:
        print(
            f'Failed to fetch image from {map_url}. Status code:', response.status_code)
        return None


# Example usage:
# save_map(1, "205 E 95th St.", "New York", "NY")

# get_map_url("205 E 95th St", "New York", "NY")
