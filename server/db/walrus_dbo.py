from walrus import WalrusClient


class DBO:
    def __init__(self, publisher_url: str, aggregator_url: str):
        self.client = WalrusClient(publisher_base_url=publisher_url, aggregator_base_url=aggregator_url)

    def create_blob_from_data(self, data: bytes) -> str:
        response = self.client.put_blob(data=data)
        blob_id = response.get('newlyCreated').get('blobObject').get('blobId')
        return blob_id

    def create_blob_from_file(self, file_path: str) -> str:
        response = self.client.put_blob_from_file(file_path)
        blob_id = response.get('newlyCreated').get('blobObject').get('blobId')
        return blob_id

    def get_blob_data(self, blob_id: str) -> str:
        blob_content = self.client.get_blob(blob_id)
        return blob_content.decode('utf-8')
    

if __name__ == "__main__":
    publisher_url = "http://walrus-publisher-testnet.haedal.xyz:9001"
    aggregator_url = "https://aggregator.testnet.walrus.mirai.cloud"
    client = DBO(publisher_base_url=publisher_url, aggregator_base_url=aggregator_url)
    data = b"Hello Walrus!"
    blob_id = client.create_blob_from_data(data)
    stored_data = client.get_blob_data(blob_id)
    if not stored_data == data.decode('utf-8'):
        raise ValueError("Data mismatch!")
    file_path = "/workspaces/btchd/data/demoCitiesWithGeoJSON.json"
    blob_id = client.create_blob_from_file(file_path)
    stored_data = client.get_blob_data(blob_id)
    with open(file_path, "r", encoding="utf-8") as f:
        original_data = f.read()
    if not stored_data == original_data:
        raise ValueError("Data mismatch!")
