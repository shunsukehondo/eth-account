# coding=utf-8

import os
import pytest

from cytoolz import (
    dissoc,
)
from eth_keyfile.keyfile import (
    get_default_work_factor_for_kdf,
)
from eth_keys import (
    keys,
)
from eth_utils import (
    is_checksum_address,
    to_bytes,
    to_hex,
    to_int,
)
from hexbytes import (
    HexBytes,
)

from eth_account import (
    Account,
)
from eth_account.messages import (
    defunct_hash_message,
)

# from https://github.com/ethereum/tests/blob/3930ca3a9a377107d5792b3e7202f79c688f1a67/BasicTests/txtest.json # noqa: 501
ETH_TEST_TRANSACTIONS = [
    {
        "chainId": None,
        "key": "c85ef7d79691fe79573b1a7064c19c1a9819ebdbd1faaab1a8ec92344438aaf4",
        "nonce": 0,
        "gasPrice": 1000000000000,
        "gas": 10000,
        "to": "0x13978aee95f38490e9769C39B2773Ed763d9cd5F",
        "value": 10000000000000000,
        "data": "",
        "unsigned": "eb8085e8d4a510008227109413978aee95f38490e9769c39b2773ed763d9cd5f872386f26fc1000080808080",  # noqa: 501
        "signed": "f86b8085e8d4a510008227109413978aee95f38490e9769c39b2773ed763d9cd5f872386f26fc10000801ba0eab47c1a49bf2fe5d40e01d313900e19ca485867d462fe06e139e3a536c6d4f4a014a569d327dcda4b29f74f93c0e9729d2f49ad726e703f9cd90dbb0fbf6649f1"  # noqa: 501
    },
    {
        "chainId": None,
        "key": "c87f65ff3f271bf5dc8643484f66b200109caffe4bf98c4cb393dc35740b28c0",
        "nonce": 0,
        "gasPrice": 1000000000000,
        "gas": 10000,
        "to": "",
        "value": 0,
        "data": "6025515b525b600a37f260003556601b596020356000355760015b525b54602052f260255860005b525b54602052f2",  # noqa: 501
        "unsigned": "f83f8085e8d4a510008227108080af6025515b525b600a37f260003556601b596020356000355760015b525b54602052f260255860005b525b54602052f2808080",  # noqa: 501
        "signed": "f87f8085e8d4a510008227108080af6025515b525b600a37f260003556601b596020356000355760015b525b54602052f260255860005b525b54602052f21ba05afed0244d0da90b67cf8979b0f246432a5112c0d31e8d5eedd2bc17b171c694a0bb1035c834677c2e1185b8dc90ca6d1fa585ab3d7ef23707e1a497a98e752d1b"  # noqa: 501
    },
    {
        "chainId": None,
        "key": "c85ef7d79691fe79573b1a7064c19c1a9819ebdbd1faaab1a8ec92344438aaf4",
        "nonce": 0,
        "gasPrice": 1000000000000,
        "gas": 10000,
        "to": HexBytes("0x13978aee95f38490e9769C39B2773Ed763d9cd5F"),
        "value": 10000000000000000,
        "data": "",
        "unsigned": "eb8085e8d4a510008227109413978aee95f38490e9769c39b2773ed763d9cd5f872386f26fc1000080808080",  # noqa: 501
        "signed": "f86b8085e8d4a510008227109413978aee95f38490e9769c39b2773ed763d9cd5f872386f26fc10000801ba0eab47c1a49bf2fe5d40e01d313900e19ca485867d462fe06e139e3a536c6d4f4a014a569d327dcda4b29f74f93c0e9729d2f49ad726e703f9cd90dbb0fbf6649f1"  # noqa: 501
    },
]


PRIVATE_KEY_AS_BYTES = b'unicorns' * 4
PRIVATE_KEY_AS_HEXSTR = '0x756e69636f726e73756e69636f726e73756e69636f726e73756e69636f726e73'
PRIVATE_KEY_AS_INT = 0x756e69636f726e73756e69636f726e73756e69636f726e73756e69636f726e73
PRIVATE_KEY_AS_OBJ = keys.PrivateKey(PRIVATE_KEY_AS_BYTES)
ACCT_ADDRESS = '0xa79F6f349C853F9Ea0B29636779ae3Cb4E3BA729'

PRIVATE_KEY_AS_BYTES_ALT = b'rainbows' * 4
PRIVATE_KEY_AS_HEXSTR_ALT = '0x7261696e626f77737261696e626f77737261696e626f77737261696e626f7773'
PRIVATE_KEY_AS_INT_ALT = 0x7261696e626f77737261696e626f77737261696e626f77737261696e626f7773
PRIVATE_KEY_AS_OBJ_ALT = keys.PrivateKey(PRIVATE_KEY_AS_BYTES_ALT)
ACCT_ADDRESS_ALT = '0xafd7f0E16A1814B854b45f551AFD493BE5F039F9'


@pytest.fixture(params=[PRIVATE_KEY_AS_INT, PRIVATE_KEY_AS_HEXSTR, PRIVATE_KEY_AS_BYTES, PRIVATE_KEY_AS_OBJ])  # noqa: 501
def PRIVATE_KEY(request):
    return request.param


@pytest.fixture(params=[PRIVATE_KEY_AS_INT_ALT, PRIVATE_KEY_AS_HEXSTR_ALT, PRIVATE_KEY_AS_BYTES_ALT, PRIVATE_KEY_AS_OBJ_ALT])  # noqa: 501
def PRIVATE_KEY_ALT(request):
    return request.param


@pytest.fixture
def acct(request):
    return Account


@pytest.fixture(params=("text", "primitive", "hexstr"))
def signature_kwargs(request):
    if request == "text":
        return {"text": "hello world"}
    elif request == "primitive":
        return {"primitive": b"hello world"}
    else:
        return {"hexstr": "68656c6c6f20776f726c64"}


def test_eth_account_default_kdf(acct, monkeypatch):
    assert os.getenv('ETH_ACCOUNT_KDF') is None
    assert acct.default_kdf == 'scrypt'

    monkeypatch.setenv('ETH_ACCOUNT_KDF', 'pbkdf2')
    assert os.getenv('ETH_ACCOUNT_KDF') == 'pbkdf2'

    import importlib
    from eth_account import account
    importlib.reload(account)
    assert account.Account.default_kdf == 'pbkdf2'


def test_eth_account_create_variation(acct):
    account1 = acct.create()
    account2 = acct.create()
    assert account1 != account2


def test_eth_account_equality(acct, PRIVATE_KEY):
    acct1 = acct.privateKeyToAccount(PRIVATE_KEY)
    acct2 = acct.privateKeyToAccount(PRIVATE_KEY)
    assert acct1 == acct2


def test_eth_account_privateKeyToAccount_reproducible(acct, PRIVATE_KEY):
    account1 = acct.privateKeyToAccount(PRIVATE_KEY)
    account2 = acct.privateKeyToAccount(PRIVATE_KEY)
    assert bytes(account1) == PRIVATE_KEY_AS_BYTES
    assert bytes(account1) == bytes(account2)
    assert isinstance(str(account1), str)


def test_eth_account_privateKeyToAccount_diverge(acct, PRIVATE_KEY, PRIVATE_KEY_ALT):
    account1 = acct.privateKeyToAccount(PRIVATE_KEY)
    account2 = acct.privateKeyToAccount(PRIVATE_KEY_ALT)
    assert bytes(account2) == PRIVATE_KEY_AS_BYTES_ALT
    assert bytes(account1) != bytes(account2)


def test_eth_account_privateKeyToAccount_seed_restrictions(acct):
    with pytest.raises(ValueError):
        acct.privateKeyToAccount(b'')
    with pytest.raises(ValueError):
        acct.privateKeyToAccount(b'\xff' * 31)
    with pytest.raises(ValueError):
        acct.privateKeyToAccount(b'\xff' * 33)


def test_eth_account_privateKeyToAccount_properties(acct, PRIVATE_KEY):
    account = acct.privateKeyToAccount(PRIVATE_KEY)
    assert callable(account.signHash)
    assert callable(account.signTransaction)
    assert is_checksum_address(account.address)
    assert account.address == ACCT_ADDRESS
    assert account.privateKey == PRIVATE_KEY_AS_OBJ


def test_eth_account_create_properties(acct):
    account = acct.create()
    assert callable(account.signHash)
    assert callable(account.signTransaction)
    assert is_checksum_address(account.address)
    assert isinstance(account.privateKey, bytes) and len(account.privateKey) == 32


def test_eth_account_recover_transaction_example(acct):
    raw_tx_hex = '0xf8640d843b9aca00830e57e0945b2063246f2191f18f2675cedb8b28102e957458018025a00c753084e5a8290219324c1a3a86d4064ded2d15979b1ea790734aaa2ceaafc1a0229ca4538106819fd3a5509dd383e8fe4b731c6870339556a5c06feb9cf330bb'  # noqa: E501
    from_account = acct.recoverTransaction(raw_tx_hex)
    assert from_account == '0xFeC2079e80465cc8C687fFF9EE6386ca447aFec4'


def test_eth_account_recover_transaction_with_literal(acct):
    raw_tx = 0xf8640d843b9aca00830e57e0945b2063246f2191f18f2675cedb8b28102e957458018025a00c753084e5a8290219324c1a3a86d4064ded2d15979b1ea790734aaa2ceaafc1a0229ca4538106819fd3a5509dd383e8fe4b731c6870339556a5c06feb9cf330bb  # noqa: E501
    from_account = acct.recoverTransaction(raw_tx)
    assert from_account == '0xFeC2079e80465cc8C687fFF9EE6386ca447aFec4'


def test_eth_account_recover_message(acct):
    v, r, s = (
        28,
        '0xe6ca9bba58c88611fad66a6ce8f996908195593807c4b38bd528d2cff09d4eb3',
        '0x3e5bfbbf4d3e39b1a2fd816a7680c19ebebaf3a141b239934ad43cb33fcec8ce',
    )
    message = "I♥SF"
    msghash = defunct_hash_message(text=message)
    from_account = acct.recoverHash(msghash, vrs=(v, r, s))
    assert from_account == '0x5ce9454909639D2D17A3F753ce7d93fa0b9aB12E'


@pytest.mark.parametrize(
    'signature_bytes',
    [
        # test signature bytes with standard v (0 in this case)
        b'\x0cu0\x84\xe5\xa8)\x02\x192L\x1a:\x86\xd4\x06M\xed-\x15\x97\x9b\x1e\xa7\x90sJ\xaa,\xea\xaf\xc1"\x9c\xa4S\x81\x06\x81\x9f\xd3\xa5P\x9d\xd3\x83\xe8\xfeKs\x1chp3\x95V\xa5\xc0o\xeb\x9c\xf30\xbb\x00',  # noqa: E501
        # test signature bytes with chain-naive v (27 in this case)
        b'\x0cu0\x84\xe5\xa8)\x02\x192L\x1a:\x86\xd4\x06M\xed-\x15\x97\x9b\x1e\xa7\x90sJ\xaa,\xea\xaf\xc1"\x9c\xa4S\x81\x06\x81\x9f\xd3\xa5P\x9d\xd3\x83\xe8\xfeKs\x1chp3\x95V\xa5\xc0o\xeb\x9c\xf30\xbb\x1b',  # noqa: E501
    ],
    ids=['test_sig_bytes_standard_v', 'test_sig_bytes_chain_naive_v']
)
def test_eth_account_recover_signature_bytes(acct, signature_bytes):
    msg_hash = b'\xbb\r\x8a\xba\x9f\xf7\xa1<N,s{i\x81\x86r\x83{\xba\x9f\xe2\x1d\xaa\xdd\xb3\xd6\x01\xda\x00\xb7)\xa1'  # noqa: E501
    from_account = acct.recoverHash(msg_hash, signature=signature_bytes)
    assert from_account == '0xFeC2079e80465cc8C687fFF9EE6386ca447aFec4'


def test_eth_account_recover_vrs(acct):
    v, r, s = (
        27,
        5634810156301565519126305729385531885322755941350706789683031279718535704513,
        15655399131600894366408541311673616702363115109327707006109616887384920764603,
    )
    msg_hash = b'\xbb\r\x8a\xba\x9f\xf7\xa1<N,s{i\x81\x86r\x83{\xba\x9f\xe2\x1d\xaa\xdd\xb3\xd6\x01\xda\x00\xb7)\xa1'  # noqa: E501
    from_account = acct.recoverHash(msg_hash, vrs=(v, r, s))
    assert from_account == '0xFeC2079e80465cc8C687fFF9EE6386ca447aFec4'

    from_account = acct.recoverHash(msg_hash, vrs=map(to_hex, (v, r, s)))
    assert from_account == '0xFeC2079e80465cc8C687fFF9EE6386ca447aFec4'


def test_eth_account_recover_vrs_standard_v(acct):
    v, r, s = (
        0,
        5634810156301565519126305729385531885322755941350706789683031279718535704513,
        15655399131600894366408541311673616702363115109327707006109616887384920764603,
    )
    msg_hash = b'\xbb\r\x8a\xba\x9f\xf7\xa1<N,s{i\x81\x86r\x83{\xba\x9f\xe2\x1d\xaa\xdd\xb3\xd6\x01\xda\x00\xb7)\xa1'  # noqa: E501
    from_account = acct.recoverHash(msg_hash, vrs=(v, r, s))
    assert from_account == '0xFeC2079e80465cc8C687fFF9EE6386ca447aFec4'


@pytest.mark.parametrize(
    'message, expected',
    [
        (
            'Message tö sign. Longer than hash!',
            HexBytes('0x10c7cb57942998ab214c062e7a57220a174aacd80418cead9f90ec410eacada1'),
        ),
        (
            # Intentionally sneaky: message is a hexstr interpreted as text
            '0x4d6573736167652074c3b6207369676e2e204c6f6e676572207468616e206861736821',
            HexBytes('0x6192785e9ad00100e7332ff585824b65eafa30bc8f1265cf86b5368aa3ab5d56'),
        ),
        (
            'Hello World',
            HexBytes('0xa1de988600a42c4b4ab089b619297c17d53cffae5d5120d82d8a92d0bb3b78f2'),
        ),
    ],
    ids=['message_to_sign', 'hexstr_as_text', 'hello_world']
)
def test_eth_account_hash_message_text(message, expected):
    assert defunct_hash_message(text=message) == expected


@pytest.mark.parametrize(
    'message, expected',
    [
        (
            '0x4d6573736167652074c3b6207369676e2e204c6f6e676572207468616e206861736821',
            HexBytes('0x10c7cb57942998ab214c062e7a57220a174aacd80418cead9f90ec410eacada1'),
        ),
        (
            '0x29d9f7d6a1d1e62152f314f04e6bd4300ad56fd72102b6b83702869a089f470c',
            HexBytes('0xe709159ef0e6323c705786fc50e47a8143812e9f82f429e585034777c7bf530b'),
        ),
    ],
    ids=['hexbytes_1', 'hexbytes_2']
)
def test_eth_account_hash_message_hexstr(acct, message, expected):
    assert defunct_hash_message(hexstr=message) == expected


@pytest.mark.parametrize(
    'message, key, expected_bytes, expected_hash, v, r, s, signature',
    (
        (
            'Some data',
            '0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318',
            b'Some data',
            HexBytes('0x1da44b586eb0729ff70a73c326926f6ed5a25f5b056e7f47fbc6e58d86871655'),
            28,
            83713930994764734002432606962255364472443135907807238282514898577139886061053,
            43435997768575461196683613590576722655951133545204789519877940758262837256233,
            HexBytes('0xb91467e570a6466aa9e9876cbcd013baba02900b8979d43fe208a4a4f339f5fd6007e74cd82e037b800186422fc2da167c747ef045e5d18a5f5d4300f8e1a0291c'),  # noqa: E501
        ),
        (
            'Some data',
            keys.PrivateKey(HexBytes('0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318')),  # noqa: E501
            b'Some data',
            HexBytes('0x1da44b586eb0729ff70a73c326926f6ed5a25f5b056e7f47fbc6e58d86871655'),
            28,
            83713930994764734002432606962255364472443135907807238282514898577139886061053,
            43435997768575461196683613590576722655951133545204789519877940758262837256233,
            HexBytes('0xb91467e570a6466aa9e9876cbcd013baba02900b8979d43fe208a4a4f339f5fd6007e74cd82e037b800186422fc2da167c747ef045e5d18a5f5d4300f8e1a0291c'),  # noqa: E501
        ),
        (
            '10284',
            '0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318',
            b'10284',
            HexBytes('0x0a162a5efbba02f38db3114531c8acba39fe676f09f7e471d93e8a06c471821c'),
            27,
            143748089818580655331728101695676826715814583506606354117109114714663470502,
            227853308212209543997879651656855994238138056366857653269155208245074180053,
            HexBytes('0x00515bc8fd32264e21ec0820e8c5123ed58c1195c9ea17cb018b1ad4073cc5a60080f5dcec397a5a8c523082bfa41771568903aa554ec06ba8475ca9050fb7d51b'),  # noqa: E501
        ),

    ),
    ids=['web3js_hex_str_example', 'web3js_eth_keys.datatypes.PrivateKey_example', '31byte_r_and_s'],  # noqa: E501
)
def test_eth_account_sign(acct, message, key, expected_bytes, expected_hash, v, r, s, signature):
    msghash = defunct_hash_message(text=message)
    assert msghash == expected_hash
    signed = acct.signHash(msghash, private_key=key)
    assert signed.messageHash == expected_hash
    assert signed.v == v
    assert signed.r == r
    assert signed.s == s
    assert signed.signature == signature

    account = acct.privateKeyToAccount(key)
    msghash = defunct_hash_message(text=message)
    assert account.signHash(msghash) == signed


def test_eth_valid_account_address_sign_data_with_intended_validator(acct, signature_kwargs):
    account = acct.create()
    hashed_msg = defunct_hash_message(
        **signature_kwargs,
        signature_version=b'\x00',
        version_specific_data=account.address,
    )
    signed = acct.signHash(hashed_msg, account.privateKey)
    new_addr = acct.recoverHash(hashed_msg, signature=signed.signature)
    assert new_addr == account.address


def test_eth_short_account_address_sign_data_with_intended_validator(acct, signature_kwargs):
    account = acct.create()

    address_in_bytes = to_bytes(hexstr=account.address)
    # Test for all lengths of addresses < 20 bytes
    for i in range(1, 21):
        with pytest.raises(TypeError):
            # Raise TypeError if the address is less than 20 bytes
            defunct_hash_message(
                **signature_kwargs,
                signature_version=b'\x00',
                version_specific_data=to_hex(address_in_bytes[:-i]),
            )


def test_eth_long_account_address_sign_data_with_intended_validator(acct, signature_kwargs):
    account = acct.create()

    address_in_bytes = to_bytes(hexstr=account.address)
    with pytest.raises(TypeError):
        # Raise TypeError if the address is more than 20 bytes
        defunct_hash_message(
            **signature_kwargs,
            signature_version=b'\x00',
            version_specific_data=to_hex(address_in_bytes + b'\x00'),
        )


@pytest.mark.parametrize(
    'txn, private_key, expected_raw_tx, tx_hash, r, s, v',
    (
        (
            {
                'to': '0xF0109fC8DF283027b6285cc889F5aA624EaC1F55',
                'value': 1000000000,
                'gas': 2000000,
                'gasPrice': 234567897654321,
                'nonce': 0,
                'chainId': 1
            },
            '0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318',
            HexBytes('0xf86a8086d55698372431831e848094f0109fc8df283027b6285cc889f5aa624eac1f55843b9aca008025a009ebb6ca057a0535d6186462bc0b465b561c94a295bdb0621fc19208ab149a9ca0440ffd775ce91a833ab410777204d5341a6f9fa91216a6f3ee2c051fea6a0428'),  # noqa: E501
            HexBytes('0xd8f64a42b57be0d565f385378db2f6bf324ce14a594afc05de90436e9ce01f60'),
            4487286261793418179817841024889747115779324305375823110249149479905075174044,
            30785525769477805655994251009256770582792548537338581640010273753578382951464,
            37,
        ),
        (
            {
                'to': '0xF0109fC8DF283027b6285cc889F5aA624EaC1F55',
                'value': 1000000000,
                'gas': 2000000,
                'gasPrice': 234567897654321,
                'nonce': 0,
                'chainId': 1
            },
            keys.PrivateKey(HexBytes('0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318')),  # noqa: E501
            HexBytes('0xf86a8086d55698372431831e848094f0109fc8df283027b6285cc889f5aa624eac1f55843b9aca008025a009ebb6ca057a0535d6186462bc0b465b561c94a295bdb0621fc19208ab149a9ca0440ffd775ce91a833ab410777204d5341a6f9fa91216a6f3ee2c051fea6a0428'),  # noqa: E501
            HexBytes('0xd8f64a42b57be0d565f385378db2f6bf324ce14a594afc05de90436e9ce01f60'),
            4487286261793418179817841024889747115779324305375823110249149479905075174044,
            30785525769477805655994251009256770582792548537338581640010273753578382951464,
            37,
        ),
        (
            {
                'to': '0xF0109fC8DF283027b6285cc889F5aA624EaC1F55',
                'value': 0,
                'gas': 31853,
                'gasPrice': 0,
                'nonce': 0,
                'chainId': 1
            },
            '0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318',
            HexBytes('0xf85d8080827c6d94f0109fc8df283027b6285cc889f5aa624eac1f558080269f22f17b38af35286ffbb0c6376c86ec91c20ecbad93f84913a0cc15e7580cd99f83d6e12e82e3544cb4439964d5087da78f74cefeec9a450b16ae179fd8fe20'),  # noqa: E501
            HexBytes('0xb0c5e2c6b29eeb0b9c1d63eaa8b0f93c02ead18ae01cb7fc795b0612d3e9d55a'),
            61739443115046231975538240097110168545680205678104352478922255527799426265,
            232940010090391255679819602567388136081614408698362277324138554019997613600,
            38,
        ),
    ),
    ids=['web3js_hex_str_example', 'web3js_eth_keys.datatypes.PrivateKey_example', '31byte_r_and_s'],  # noqa: E501
)
def test_eth_account_sign_transaction(acct, txn, private_key, expected_raw_tx, tx_hash, r, s, v):
    signed = acct.signTransaction(txn, private_key)
    assert signed.r == r
    assert signed.s == s
    assert signed.v == v
    assert signed.rawTransaction == expected_raw_tx
    assert signed.hash == tx_hash

    account = acct.privateKeyToAccount(private_key)
    assert account.signTransaction(txn) == signed


@pytest.mark.parametrize(
    'transaction',
    ETH_TEST_TRANSACTIONS,
)
def test_eth_account_sign_transaction_from_eth_test(acct, transaction):
    expected_raw_txn = transaction['signed']
    key = transaction['key']

    unsigned_txn = dissoc(transaction, 'key', 'signed', 'unsigned')

    # validate r, in order to validate the transaction hash
    # There is some ambiguity about whether `r` will always be deterministically
    # generated from the transaction hash and private key, mostly due to code
    # author's ignorance. The example test fixtures and implementations seem to agree, so far.
    # See ecdsa_raw_sign() in /eth_keys/backends/native/ecdsa.py
    signed = acct.signTransaction(unsigned_txn, key)
    assert signed.r == to_int(hexstr=expected_raw_txn[-130:-66])

    # confirm that signed transaction can be recovered to the sender
    expected_sender = acct.privateKeyToAccount(key).address
    assert acct.recoverTransaction(signed.rawTransaction) == expected_sender


@pytest.mark.parametrize(
    'transaction',
    ETH_TEST_TRANSACTIONS,
)
def test_eth_account_recover_transaction_from_eth_test(acct, transaction):
    raw_txn = transaction['signed']
    key = transaction['key']
    expected_sender = acct.privateKeyToAccount(key).address
    assert acct.recoverTransaction(raw_txn) == expected_sender


def get_encrypt_test_params():
    """
    Params for testing Account#encrypt. Due to not being able to provide fixtures to
    pytest.mark.parameterize, we opt for creating the params in a non-fixture method
    here instead of providing fixtures for the private key and password.
    """
    key = '0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318'
    key_bytes = to_bytes(hexstr=key)
    private_key = keys.PrivateKey(HexBytes(key))
    password = 'test!'

    # 'private_key, password, kdf, iterations, expected_decrypted_key, expected_kdf'
    return [
        (
            key,
            password,
            None,
            None,
            key_bytes,
            'scrypt'
        ),
        (
            private_key,
            password,
            None,
            None,
            private_key.to_bytes(),
            'scrypt'
        ),
        (
            key,
            password,
            'pbkdf2',
            None,
            key_bytes,
            'pbkdf2'
        ),
        (
            key,
            password,
            None,
            1024,
            key_bytes,
            'scrypt'
        ),
        (
            key,
            password,
            'pbkdf2',
            1024,
            key_bytes,
            'pbkdf2'
        ),
        (
            key,
            password,
            'scrypt',
            1024,
            key_bytes,
            'scrypt'
        ),
    ]


@pytest.mark.parametrize(
    'private_key, password, kdf, iterations, expected_decrypted_key, expected_kdf',
    get_encrypt_test_params(),
    ids=[
        'hex_str',
        'eth_keys.datatypes.PrivateKey',
        'hex_str_provided_kdf',
        'hex_str_default_kdf_provided_iterations',
        'hex_str_pbkdf2_provided_iterations',
        'hex_str_scrypt_provided_iterations',
    ]
)
def test_eth_account_encrypt(
        acct,
        private_key,
        password,
        kdf,
        iterations,
        expected_decrypted_key,
        expected_kdf):
    if kdf is None:
        encrypted = acct.encrypt(private_key, password, iterations=iterations)
    else:
        encrypted = acct.encrypt(private_key, password, kdf=kdf, iterations=iterations)

    assert encrypted['address'] == '2c7536e3605d9c16a7a3d7b1898e529396a65c23'
    assert encrypted['version'] == 3
    assert encrypted['crypto']['kdf'] == expected_kdf

    if iterations is None:
        expected_iterations = get_default_work_factor_for_kdf(expected_kdf)
    else:
        expected_iterations = iterations

    if expected_kdf == 'pbkdf2':
        assert encrypted['crypto']['kdfparams']['c'] == expected_iterations
    elif expected_kdf == 'scrypt':
        assert encrypted['crypto']['kdfparams']['n'] == expected_iterations
    else:
        raise Exception("test must be upgraded to confirm iterations with kdf %s" % expected_kdf)

    decrypted_key = acct.decrypt(encrypted, password)

    assert decrypted_key == expected_decrypted_key


@pytest.mark.parametrize(
    'private_key, password, kdf, iterations, expected_decrypted_key, expected_kdf',
    get_encrypt_test_params(),
    ids=[
        'hex_str',
        'eth_keys.datatypes.PrivateKey',
        'hex_str_provided_kdf',
        'hex_str_default_kdf_provided_iterations',
        'hex_str_pbkdf2_provided_iterations',
        'hex_str_scrypt_provided_iterations',
    ]
)
def test_eth_account_prepared_encrypt(
        acct,
        private_key,
        password,
        kdf,
        iterations,
        expected_decrypted_key,
        expected_kdf):
    account = acct.privateKeyToAccount(private_key)

    if kdf is None:
        encrypted = account.encrypt(password, iterations=iterations)
    else:
        encrypted = account.encrypt(password, kdf=kdf, iterations=iterations)

    assert encrypted['address'] == '2c7536e3605d9c16a7a3d7b1898e529396a65c23'
    assert encrypted['version'] == 3
    assert encrypted['crypto']['kdf'] == expected_kdf

    if iterations is None:
        expected_iterations = get_default_work_factor_for_kdf(expected_kdf)
    else:
        expected_iterations = iterations

    if expected_kdf == 'pbkdf2':
        assert encrypted['crypto']['kdfparams']['c'] == expected_iterations
    elif expected_kdf == 'scrypt':
        assert encrypted['crypto']['kdfparams']['n'] == expected_iterations
    else:
        raise Exception("test must be upgraded to confirm iterations with kdf %s" % expected_kdf)

    decrypted_key = acct.decrypt(encrypted, password)

    assert isinstance(decrypted_key, HexBytes)
    assert decrypted_key == expected_decrypted_key
