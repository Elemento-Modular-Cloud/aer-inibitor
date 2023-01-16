import re
import subprocess

HEX_PREFIX_REGEX = re.compile('^0[xX]')
HEX_REGEX = re.compile('^(0[xX])?[0-9a-fA-F]{1,4}$')
PCIID_REGEX = re.compile('^[0-9a-fA-F]{4}:[0-9a-fA-F]{4}$')
PCIADD_REGEX = re.compile(
    '^([0-9]{0,4}:)?[0-9a-fA-F]{2}:[0-9a-fA-F]{2}.[0-9a-fA-F]{1,2}$')

PCI_EXP_DEVCTL = 8             # Default offset from the standard CAP_EXP registry
AER_TYPES_MAP = {}
AER_TYPES_MAP['corrected'] = (1, "Corrected errors")    # Which means 0x0001
AER_TYPES_MAP['nonfatal'] = (2, "Non-fatal errors")     # Which means 0x0002
AER_TYPES_MAP['fatal'] = (3, "Fatal errors")            # Which means 0x0004
AER_TYPES_MAP['unsupported'] = (4, "Unsupported errors")  # Which means 0x0008

# print(PCIID_REGEX.match("10de:1000"))
# print(PCIID_REGEX.match("10de:1000f"))
# print(PCIADD_REGEX.match("c4:00.2"))
# print(PCIADD_REGEX.match("c4:00.22"))
# print(PCIADD_REGEX.match("0000:c4:00.22"))


# def hex_to_binary(hex_code):
#     bin_code = bin(hex_code)[2:]
#     padding = (4-len(bin_code) % 4) % 4
#     return '0'*padding + bin_code


def get_setpci_base_command(pciid=None, pci_address=None):
    if not(pciid or pci_address):
        raise Exception(
            "Please provide at least an univocal pciid or pci address.")

    if pciid:
        if not PCIID_REGEX.match(pciid):
            raise Exception(
                f"Provided pciid {pciid} does not match the typical pciid pattern (FFFF:FFFF)")

    if pci_address:
        if not PCIADD_REGEX.match(pci_address):
            raise Exception(
                f"Provided pci address {pci_address} does not match the typical pci address pattern ([FFFF.]FF:FF.FF)")

    pciid_opt = f" -d {pciid}" if pciid else ' '
    pci_address_opt = f" -s \"{pci_address}\"" if pci_address else ' '
    setpci_command = f"setpci -v{pciid_opt}{pci_address_opt} CAP_EXP+0x{PCI_EXP_DEVCTL}.w"

    return setpci_command

# print(get_setpci_base_command(pciid="10de:1000"))
# # print(get_setpci_base_command(pciid="10de:1000f"))
# print(get_setpci_base_command(pci_address="c4:00.2"))
# print(get_setpci_base_command(pci_address="c4:00.22"))
# print(get_setpci_base_command(pci_address="0000:c4:00.22"))


def get_setpci_read_command(pciid=None, pci_address=None):
    return get_setpci_base_command(pciid=pciid, pci_address=pci_address)


def get_setpci_write_command(pciid=None, pci_address=None, value=None):
    if not value:
        raise Exception("Value to write is mandatory")

    if not HEX_REGEX.match(value):
        raise Exception("The provided value is not a valid HEX string")

    if not HEX_PREFIX_REGEX.match(value):
        value = f"0x{value}"

    return f"{get_setpci_base_command(pciid=pciid, pci_address=pci_address)}={value.upper()}"

# print(get_setpci_write_command(pciid="10de:1000", value="0E"))
# # print(get_setpci_write_command(pciid="10de:1000f", value="0E"))
# print(get_setpci_write_command(pci_address="c4:00.2", value="0E"))
# print(get_setpci_write_command(pci_address="c4:00.22", value="0E"))
# print(get_setpci_write_command(pci_address="0000:c4:00.22", value="0E"))


def run_setpci_command(cmd):
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = p.communicate()

    if(err):
        raise Exception(f"Command failed with error:/n{err.decode()}")

    return out.decode()


print(run_setpci_command(get_setpci_base_command(pciid="10de:1401")))


def get_AER_caps(pciid=None, pci_address=None, verbose=False):
    AER_caps_hex = run_setpci_command(get_setpci_read_command(pciid=pciid,
                                                              pci_address=pci_address)
                                      ).split('=')[-1].strip()
    return "0x{AER_caps_hex}"
    # AER_caps_bin = list(bin(int(f"0x{AER_caps_hex}", 0))[2:])
    # AER_cap_flags = [True if c == '1' else False for c in AER_caps_bin]

    # if verbose:
    #     for AER_type in AER_TYPES_MAP.values():
    #         print(
    #             f"{AER_type[1]} are {'enabled' if AER_caps_bin[-(AER_type[0])] == '1' else 'disabled'}")

    # return AER_cap_flags


print(get_AER_caps(pciid="10de:1401"))


def set_AER_caps(pciid=None, pci_address=None, type=None, enable=True):
    # if type not in AER_TYPES_MAP.keys():
        # raise Exception(f"Provided type {type} is not supported. Valid types are {', '.join(AER_TYPES_MAP.keys())}")
    # wanted_AER_cap_index = AER_TYPES_MAP[type][0]

    AER_cap_flags = get_AER_caps(pciid=pciid, pci_address=pci_address)
    AER_caps_bin = list(bin(int(AER_cap_flags, 0))[2:])
    new_AER_cap_bin = AER_caps_bin
    new_AER_cap_bin[-wanted_AER_cap_index] = '1' if enable else '0'

    new_AER_cap_flags = hex(int(new_AER_cap_bin, 2))

    print(new_AER_cap_flags)

    # AER_caps_hex = run_setpci_command(get_setpci_write_command(pciid=pciid, pci_address=pci_address, value=new_AER_cap_flags))


print(set_AER_caps(pciid="10de:1401"))


def set_enabled_AER_type(pciid=None, pci_address=None, type=None):
    return set_AER_caps(pciid=None, pci_address=None, type=None, enable=True)


def set_disabled_AER_type(pciid=None, pci_address=None, type=None):
    return set_AER_caps(pciid=None, pci_address=None, type=None, enable=False)
