# aer-inibitor
A small tool capable of inhibiting AER for specific devices.

## Rationale
Advanced Error Reporting (AER) technologies are incredibly useful to get PCIe errors on supported devices.
Many time a poor adapter might lead to a ton of `corrected` errors which easily fill up the log space.

While the kernel offers an handle to disable that for all devices, namely `pci=noaer`, it is not a wise choice, since it might hide higher severity errors.

A per-device or per-slot AER is very much needed to be able to asses corrected errors on specific devices.

## How to use
Most of the work is based on https://gist.github.com/Brainiarc7/3179144393747f35e5155fdbfd675554

Refer to the original link for the main explanation.

This repository contains a python code snippet capable of wrapping around the `setpci` util and to improve it's usability with manageable python bindings.

### AER levels
AER provides four levels:
- `corrected`: an error which gets automatically corrected
- 'non-fatal': an error which while uncorrected doesn't prevent the working order of the device
- `fatal`: oh, you don't want to get this...
- `unsupported`: the name speaks by itself

### Toggle specific AER levels
Two main functions are the main bindings most of the people would need to use: `enable_AER_type` and `disable_AER_type`.

Both functions take as parameters at least a PCIID or a PCI address (or both for better granularity) and a `type` parameter which should correspond to one of `corrected`, `non-fatal`, `fatal` or `unsupported`.

As an example one can switch off the AER `corrected` errors on device with PCIID `10de:1401` at slot `0000:c4:00.0` by running:

```python
disable_AER_type(pciid="10de:1401", pci_address="0000:c4:00.0", type="corrected")
```

If a device has disabled `fatal` reporting, and one wants to enable them, one can simply run:

```python
enable_AER_type(pciid="10de:1401", pci_address="0000:c4:00.0", type="fatal")
```

To verify the successful application of the command one can stick back to the `setpci` utility:

```bash
$: setpci -v -d 10de:1401 -s "0000:c4:00.0" CAP_EXP+0x8.w
0000:01:00.0 (cap 10 @78) @80 = 2937
```

## Config file
This tool supports a `yaml` config file tom apply AER patches at boot by means of a chronjob or a service.

The file has the following syntax:

```Dockerfile=
devices:
    - pciid: "10de:1401"
      flags:
      - aer_type: corrected
        enabled: False
    - pciid: "10de:24b0"
      pci_address: "0000:c4:00.0"
      flags:
      - aer_type: non-fatal
        enabled: True
```

## Conclusion
Thanks to this
