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
AER_TYPES_MAP['unsupported'] = (4, "Unsupported errors")# Which means 0x0008

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


def get_enabled_AER_type(pciid=None, pci_address=None):
    AER_caps_hex = run_setpci_command(get_setpci_base_command(pciid=pciid, pci_address=pci_address)).split('=')[-1].strip()
    print(AER_caps_hex)
    AER_caps_bin = list(bin(int(f"0x{AER_caps_hex}", 0))[2:])[-len(AER_TYPES_MAP):]
    print(AER_caps_bin)
    AER_caps_flag = map(True if c == '1' else False, AER_caps_bin)
    # for AER_type in AER_TYPES_MAP.values():
        # print(f"{AER_type[1]} are {'enabled' if AER_caps_bin[-(AER_type[0])] == '1' else 'disabled'}")


print(get_enabled_AER_type(pciid="10de:1401"))