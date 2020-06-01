from .objects import Server, Zone, RRSet, Record, Comment, Cryptokey, Metadata, SearchResult, StatisticItem, \
    MapStatisticItem, RingStatisticItem, SimpleStatisticItem, CacheFlushResult
from .exceptions import PDNSApiException, PDNSApiNotFound

import json
from functools import partial
import requests
import logging

logger = logging.getLogger(__name__)


# TODO:
# - Logging
# - TSIGKeys

class APIClient:

    def __init__(self, api_host, api_key, tls_verify=True, request_timeout=None):
        self._api_url = api_host if 'api/v1' in api_host else f"{api_host}/api/v1"
        self._api_key = api_key
        self._tls_verify = tls_verify
        self._request_timeout = request_timeout

        if not self._tls_verify:
            logger.warning("Disabling TLS certificate validation.")
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.request_headers = {'X-API-Key': self._api_key}

        self.get = partial(self.request, method='GET')
        self.post = partial(self.request, method='POST')
        self.put = partial(self.request, method='PUT')
        self.patch = partial(self.request, method='PATCH')
        self.delete = partial(self.request, method='DELETE')

        self.servers = self._set_servers()
        self.current_server = self.servers[0]
        self.zones = self._set_zones()

    def request(self, path: str, method: str, data=None, **kwargs):
        url = f"{self._api_url}/{path.lstrip('/')}"

        if data is None:
            data = {}

        response = requests.request(method,
                                    url,
                                    json=data,
                                    headers=self.request_headers,
                                    timeout=self._request_timeout,
                                    verify=self._tls_verify,
                                    **kwargs
                                    )

        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                raise (PDNSApiNotFound(e)) from None
            try:
                status_message = response.json()
                status_message = status_message.get('error', status_message.get('errors', 'Unknown error'))
            except:
                status_message = response.text
            raise PDNSApiException(response.status_code, status_message) from None
        except json.decoder.JSONDecodeError:
            return response.text

    def _set_servers(self):
        new_servers = list()
        for server in self.get('servers'):
            new_servers.append(Server(**server))
        return new_servers

    def _set_zones(self):
        new_zones = list()
        for zone in self.get(f'servers/{self.current_server.id}/zones'):
            new_zones.append(Zone(**zone))
        return new_zones

    def create_zone(self, zone: Zone):
        path = f'servers/{self.current_server.id}/zones'
        return Zone(**self.post(path, data=zone))

    # Zones
    def get_zone(self, zone_name):
        path = f'servers/{self.current_server.id}/zones/{zone_name}'
        zone = Zone(**self.get(path))
        new_rrsets = []
        for rrset in zone.rrsets:
            new_comments = []
            new_records = []
            rrset = RRSet(**rrset)
            for comment in rrset.comments:
                new_comments.append(Comment(**comment))
            for record in rrset.records:
                new_records.append(Record(**record))
            rrset.comments = new_comments
            rrset.records = new_records
            new_rrsets.append(rrset)
        zone.rrsets = new_rrsets
        return zone

    def delete_zone(self, zone_name):
        path = f'servers/{self.current_server.id}/zones/{zone_name}'
        self.delete(path)

    def update_zone_metadata(self, zone: Zone):
        path = f'servers/{self.current_server.id}/zones/{zone.name}'
        self.put(path, data=zone)
        return self.get_zone(zone.name)

    def patch_rrsets(self, zone: Zone):
        path = f'servers/{self.current_server.id}/zones/{zone.name}'
        self.patch(path, data={'rrsets': zone.rrsets})
        return self.get_zone(zone.name)

    def create_records(self, zone: Zone, rrsets: list):
        for rrset in rrsets:
            rrset.changetype = 'REPLACE'

        zone = Zone(name=zone.name, kind=zone.kind, rrsets=rrsets)
        return self.patch_rrsets(zone)

    def delete_records(self, zone: Zone, rrsets: list):
        for rrset in rrsets:
            rrset.changetype = 'DELETE'

        zone = Zone(name=zone.name, kind=zone.kind, rrsets=rrsets)
        return self.patch_rrsets(zone)

    # Cryptokeys
    def get_zone_cryptokeys(self, zone: Zone):
        path = f'servers/{self.current_server.id}/zones/{zone.name}/cryptokeys'
        cryptkeys_new = []
        for cryptokey in self.get(path):
            cryptkeys_new.append(Cryptokey(**cryptokey))
        return cryptkeys_new

    def create_cryptokey(self, zone: Zone, cryptokey: Cryptokey):
        path = f'servers/{self.current_server.id}/zones/{zone.name}/cryptokeys'
        return self.post(path, data=cryptokey)

    def get_cryptokey(self, zone: Zone, key_id):
        path = f'servers/{self.current_server.id}/zones/{zone.name}/cryptokeys/{key_id}'
        return Cryptokey(**self.get(path))

    def put_cryptokey(self, zone: Zone, cryptokey: Cryptokey):
        path = f'servers/{self.current_server.id}/zones/{zone.name}/cryptokeys/{cryptokey.id}'
        self.put(path, data=cryptokey)

    # Metadata
    def get_zone_metadata(self, zone: Zone):
        path = f'servers/{self.current_server.id}/zones/{zone.name}/metadata'
        metadata_new = []
        for metadata in self.get(path):
            metadata_new.append(Metadata(**metadata))
        return metadata_new

    def create_metadata(self, zone: Zone, metadata: Metadata):
        path = f'servers/{self.current_server.id}/zones/{zone.name}/metadata'
        self.post(path, data=metadata)
        return self.get_zone_metadata(zone)

    def get_metadata(self, zone: Zone, metadata_kind):
        path = f'servers/{self.current_server.id}/zones/{zone.name}/metadata/{metadata_kind}'
        return Metadata(**self.get(path))

    def put_metadata(self, zone: Zone, metadata: Metadata):
        path = f'servers/{self.current_server.id}/zones/{zone.name}/metadata/{metadata.kind}'
        return Metadata(**self.put(path, data=metadata))

    def delete_metadata(self, zone: Zone, metadata: Metadata):
        path = f'servers/{self.current_server.id}/zones/{zone.name}/metadata/{metadata.kind}'
        self.delete(path)

    # TSIGKeys
    # FIXME TBW

    # Searching
    def search(self, query: str, max_results: int, object_type: str):
        path = f'servers/{self.current_server.id}/search-data'
        object_types = ['all', 'zone', 'record', 'comment']
        if object_type not in object_types:
            raise TypeError(f"object_type must be one of {', '.join(object_types)}")

        if not isinstance(max_results, int):
            raise TypeError("max_results needs to be an integer.")

        payload = {'q': query, 'max': max_results, 'object_type': object_type}
        new_results = []
        for result in self.get(path, params=payload):
            new_results.append(SearchResult(**result))
        return new_results

    # Statistics
    def statistics(self, statistic=None, includerings=True):
        path = f'servers/{self.current_server.id}/statistics'
        payload = {'statistic': statistic, 'includerings': includerings}
        type_map = {
            'StatisticItem': StatisticItem,
            'MapStatisticItem': MapStatisticItem,
            'RingStatisticItem': RingStatisticItem
        }
        new_statistics = []
        for item in self.get(path, params=payload):
            if item.get('type') in type_map.keys():
                new_statistic = type_map[item.get('type')](**item)
                if isinstance(new_statistic.value, list):
                    new_values = []
                    for value in new_statistic.value:
                        new_values.append(SimpleStatisticItem(**value))
                    new_statistic.value = new_values
                if statistic is not None:
                    return new_statistic
                new_statistics.append(new_statistic)
        return new_statistics

    # Cache
    def flush_cache(self, domain: str):
        path = f'servers/{self.current_server.id}/cache/flush'
        payload = {'domain': domain}
        return CacheFlushResult(**self.put(path, params=payload))
