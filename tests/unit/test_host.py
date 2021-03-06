from betamax import Betamax
from betamax_serializers.pretty_json import PrettyJSONSerializer
from ddi.cli import initiate_session
from ddi.host import *

import base64
import jsend
import os
import pytest
import url_normalize

ddi_host = os.environ.get('DDI_HOST', 'ddi-test-host.example.com')
ddi_host2 = os.environ.get('DDI_HOST2', 'ddi-test-host2.example.com')
ddi_password = os.environ.get('DDI_PASSWORD', 'test_password')
ddi_server = os.environ.get('DDI_SERVER', 'https://ddi.example.com')
ddi_site_name = os.environ.get('DDI_SITE_NAME', 'EXAMPLE')
ddi_url = url_normalize.url_normalize(ddi_server)
ddi_username = os.environ.get('DDI_USERNAME', 'test_user')
domain_name = os.environ.get('DOMAINNAME', 'example.com')

# Makes the output more readable
Betamax.register_serializer(PrettyJSONSerializer)

config = Betamax.configure()
config.cassette_library_dir = 'tests/cassettes'
config.default_cassette_options['serialize_with'] = 'prettyjson'
config.default_cassette_options['placeholders'] = [
    {
        'placeholder': '<PASSWORD>',
        'replace': base64.b64encode(ddi_password.encode()).decode()
    },
    {
        'placeholder': '<LOGIN>',
        'replace': base64.b64encode(ddi_username.encode()).decode()
    },
    {
        'placeholder': '<DDI_SERVER>',
        'replace': ddi_server
    },
    {
        'placeholder': '<DDI_HOST>',
        'replace': ddi_host
    },
    {
        'placeholder': '<DDI_HOST2>',
        'replace': ddi_host2
    },
    {
        'placeholder': 'example.com',
        'replace': domain_name
    },
    {
        'placeholder': 'EXAMPLE',
        'replace': ddi_site_name
    },
]


@pytest.fixture()
def client():
    return initiate_session(ddi_password, False, ddi_username)


def test_add_host(client):
    """
    There are two ways to add a host, one by specifying the exact IP for the
    host to use, two by specifying the subnet for the host to be on and allowing
    DDI to find a free IP on the subnet and assigning it to the host.
    """
    recorder = Betamax(client)

    with recorder.use_cassette('ddi_add_host'):
        ip_result = add_host(building='TEST', department='TEST',
                             contact='Test User', ip='172.23.23.4',
                             phone='555-1212', name=ddi_host, session=client,
                             url=ddi_url, comment='Test Comment')
        subnet_result = add_host(building='TEST', department='TEST',
                                 contact='Test User', subnet='172.23.23.0',
                                 phone='555-1212', name=ddi_host2,
                                 session=client, url=ddi_url,
                                 comment='Test Comment')

    assert isinstance(ip_result, dict)
    assert jsend.is_success(ip_result)

    assert isinstance(subnet_result, dict)
    assert jsend.is_success(subnet_result)


def test_get_host(client):
    recorder = Betamax(client)

    with recorder.use_cassette('ddi_get_host'):
        result = get_host(fqdn=ddi_host, session=client, url=ddi_url)

    assert isinstance(result, dict)
    assert jsend.is_success(result)
    assert result['data']['results'][0]['name'] == ddi_host


def test_delete_host(client):
    recorder = Betamax(client)

    with recorder.use_cassette('ddi_delete_host'):
        result = delete_host(fqdn=ddi_host, session=client, url=ddi_url)

    assert isinstance(result, dict)
    assert jsend.is_success(result)
    assert 'ret_oid' in result['data']['results'][0]
