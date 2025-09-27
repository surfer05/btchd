import geohash


def decode_geohash(hash):
    bbox = geohash.decode_exactly(hash)
    lat = (bbox[0] + bbox[2]) / 2
    lon = (bbox[1] + bbox[3]) / 2
    return lat, lon


if __name__ == "__main__":
    test_hash = "w21z7dh"
    lat, lon = decode_geohash(test_hash)
    print(f"Geohash: {test_hash} -> Latitude: {lat}, Longitude: {lon}")