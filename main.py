import requests


def geocode_address(address):
    """
    Use Nominatim (OpenStreetMap) to turn a street address into lat/lon.
    """
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": address,
        "format": "json",
        "limit": 1,
    }

    headers = {"User-Agent": "PhillyTrashApp/1.0 (gregdrew12@gmail.com)"}

    r = requests.get(url, params=params, headers=headers)
    r.raise_for_status()
    results = r.json()

    if not results:
        return None

    lat = float(results[0]["lat"])
    lon = float(results[0]["lon"])
    return lat, lon


def get_trash_day(lat, lon):
    """
    Query Philadelphia's sanitation collection boundary dataset
    to determine trash day (collday) and secondary day (if any).
    """

    url = "https://services.arcgis.com/fLeGjb7u4uXqeF9q/arcgis/rest/services/Rubbish_Recyc_Coll_Bnd/FeatureServer/0/query"

    params = {
        "geometry": f"{lon},{lat}",  # ArcGIS expects lon,lat
        "geometryType": "esriGeometryPoint",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "collday,secondary_rubbish_day,disday",
        "f": "json",
    }

    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()

    if "features" not in data or len(data["features"]) == 0:
        return None  # No match found (shouldn’t happen for valid Philly addresses)

    attrs = data["features"][0]["attributes"]

    return {
        "primary_trash_day": attrs.get("collday"),
        "secondary_trash_day": attrs.get("secondary_rubbish_day"),
        "district_code": attrs.get("disday"),
    }


def main():
    lat, lon = geocode_address("762 S 15th St, Philadelphia, PA 19146")
    info = get_trash_day(lat, lon)
    print(info)


if __name__ == "__main__":
    main()
