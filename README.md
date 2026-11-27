# NX2 Flow Universal Sender

Unofficial Windows desktop client for the Toronja transfer protocol supported by NX2 Flow. Transfers existing NUP files over a local network; compatible receivers handle FAT32 splitting. This project does not convert files or include games or keys.
## Why This Project Exists

FAT32 has a maximum individual file size of 4 GiB minus one byte, making it impossible to directly copy larger NUP files onto FAT32-formatted SD cards.

NX2 Flow Universal Sender simplifies this process by transmitting large NUP files wirelessly to the NX2 Flow receiver, which automatically handles file splitting.

### Benefits

- Transfer NUP files larger than 4 GiB.
- No manual file splitting required.
- No need to remove the SD card.
- No need to reformat the SD card.
- Live transfer progress, speed and estimated completion time.
- CRC32 transfer integrity verification.

The sender uses the existing Toronja transfer protocol and NX2 Flow's receiver-side splitting functionality, providing a convenient standalone Windows interface for the entire transfer process.

## Usage

1. Open the receiver in NX2 Flow on your console.
2. Connect the PC and console to the same trusted local network.
3. Open NX2FlowSender.exe (when available in Releases), enter the receiver IP and leave the port at 28302 unless configured differently.
4. Browse for files you are authorized to use and start the transfer. Check the CRC32 result.

The IP is remembered locally. The protocol is not encrypted; use a trusted network. Existing destination files may be replaced.

## Build on Windows

Install Python 3.14 with Tkinter, then run from this directory:

```cmd
py -3.14 -m pip install -r requirements-build.txt
py -3.14 -m PyInstaller --clean --noconfirm NX2FlowSender.spec
```

The executable appears in `dist/`. No extra Python packages are required to run the source itself.

## Status

Early beta. The original command-line prototype completed a 16.63 GiB transfer with matching CRC32. The original GUI connected and began a transfer. This revised build still requires Windows and console testing. No automatic resume or conversion is implemented.

## Credits

Olmectron — [NX2 Flow](https://github.com/Olmectron/nx2-flow) and [Toronja](https://github.com/Olmectron/toronja). This is an independent, unofficial client, not affiliated with those projects or Nintendo.
## Legal Disclaimer

NX2 Flow Universal Sender is an independently developed file-transfer utility intended for lawful homebrew, personal file management, and authorized backups.

- This project is not affiliated with, endorsed by, or sponsored by Nintendo, Olmectron, or their respective projects.
- This software does not include copyrighted games, proprietary firmware, encryption keys, or Nintendo assets.
- Users are responsible for ensuring their use of this software complies with applicable laws and intellectual property rights.
- This project does not encourage or endorse piracy, copyright infringement, or unauthorized distribution of copyrighted material.
- All trademarks belong to their respective owners.
- This software is provided "AS IS," without warranty of any kind, subject to the terms of the MIT License.
- To the extent permitted by applicable law, the developer assumes no liability for data loss, hardware damage, account restrictions, or other damages arising from use of this software.

Copyright (c) 2026 ByteRelic.
## License

This project is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.
