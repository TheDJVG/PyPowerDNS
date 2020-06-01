class _BaseObject(dict):
    required_fields = None
    optional_fields = {}

    def __init__(self, **kwargs):
        if isinstance(self.required_fields, dict):
            # Compare to make sure required fields are there
            missing_fields = set(self.required_fields.keys()) - set(kwargs.keys())
            if missing_fields:
                raise TypeError(
                    f"missing {len(missing_fields)} required positional arguments: {','.join(missing_fields)}")

            # Check for fields not specified and raise
            invalid_fields = set(kwargs.keys()) - set(
                list(self.required_fields.keys()) + list(self.optional_fields.keys()))
            if invalid_fields:
                raise TypeError(
                    f"unknown {len(invalid_fields)} positional arguments: {', '.join(invalid_fields)}")
        super(_BaseObject, self).__init__(**kwargs)
        self.__dict__ = self

    def __repr__(self):
        kv = [f"{key}={str(value)}" for key, value in self.items()]
        return f"{type(self).__name__}({', '.join(kv)})"


class Server(_BaseObject):
    required_fields = {
        'type': str,
        'id': str,
        'daemon_type': str,
        'version': str,
        'url': str,
        'config_url': str,
        'zones_url': str
    }

    def __repr__(self):
        return self.id


class Zone(_BaseObject):
    def __init__(self, **kwargs):
        super(Zone, self).__init__(**kwargs)
        if self.name[-1] != '.':
            self.name += '.'

    optional_fields = {
        'id': str,
        'type': str,
        'url': str,
        'rrsets': list,
        'serial': int,
        'notified_serial': int,
        'edited_serial': int,
        'masters': list,
        'dnssec': bool,
        'nsec3param': str,
        'nsec3narrow': bool,
        'presigned': bool,
        'soa_edit': str,
        'soa_edit_api': str,
        'api_rectify': bool,
        'zone': str,
        'account': str,
        'nameservers': list,
        'master_tsig_key_ids': list,
        'slave_tsig_key_ids': list,
        'last_check': int
    }
    required_fields = {
        'name': str,
        'kind': str,
    }

    def __repr__(self):
        return self.name


class RRSet(_BaseObject):
    def __init__(self, **kwargs):
        super(RRSet, self).__init__(**kwargs)
        if self.name[-1] != '.':
            self.name += '.'

    optional_fields = {
        'records': list,
        'comments': list,
        'changetype': str,

    }
    required_fields = {
        'name': str,
        'ttl': int,
        'type': str,
    }


class Record(_BaseObject):
    required_fields = {
        'content': str,
        'disabled': bool,
    }


class Comment(_BaseObject):
    optional_fields = {
        'account': str,
        'modified_at': int,
    }
    required_fields = {
        'content': str,
    }


class Cryptokey(_BaseObject):
    optional_fields = {
        'privatekey': str,
        'flags': str,
        'id': int,
        'type': str,
        'published': bool,
        'dnskey': str,
        'ds': list,
        'algorithm': str,
        'bits': int,

    }

    required_fields = {
        'active': bool,
        'keytype': str,
    }


class Metadata(_BaseObject):
    optional_fields = {
        'type': str,
    }
    required_fields = {
        'kind': str,
        'metadata': list
    }


class TSIGKey(_BaseObject):
    optional_fields = {
        'id': str,
        'key': str,
        'type': str,

    }
    required_fields = {
        'name': str,
        'algorithm': str,
    }


class SearchResult(_BaseObject):
    optional_fields = {
        'content': str,
        'disabled': bool,
        'zone': str,
        'type': str,
        'ttl': int,
    }

    required_fields = {
        'name': str,
        'object_type': str,
        'zone_id': str,
    }


class StatisticItem(_BaseObject):
    required_fields = {
        'name': str,
        'type': str,
        'value': str,
    }


class MapStatisticItem(_BaseObject):
    required_fields = {
        'name': str,
        'type': str,
        'value': str,
    }


class RingStatisticItem(_BaseObject):
    required_fields = {
        'name': str,
        'type': str,
        'size': int,
        'value': str,
    }


class SimpleStatisticItem(_BaseObject):
    required_fields = {
        'name': str,
        'value': str,
    }


class CacheFlushResult(_BaseObject):
    required_fields = {
        'count': float,
        'result': str,
    }
