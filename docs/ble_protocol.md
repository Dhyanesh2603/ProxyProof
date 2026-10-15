# ProxyProof Bluetooth Low Energy (BLE) Protocol Specification

## 1. Physical Layer & Broadcasting Paradigm

ProxyProof operates strictly on **connectionless BLE Advertising (Broadcaster / Observer)**. 
Traditional Bluetooth pairing introduces high connection latency ($2\text{--}5\text{ seconds}$ per peer) and a maximum physical limit of 7--8 concurrent connections per master radio. ProxyProof solves this scalability bottleneck:

- The **Organizer Device (Instructor phone/beacon)** acts as a non-connectable, undirected broadcaster (`ADV_NONCONN_IND`).
- Up to **thousands of student devices** observe advertising packets simultaneously with zero connection overhead.

---

## 2. Packet Layout (Standard 31-Byte Legacy BLE Frame)

Legacy BLE advertising frames allocate a maximum payload of **31 bytes**. ProxyProof packs its cryptographic payload into **26 bytes**, fitting comfortably without requiring a secondary `SCAN_RSP` (Scan Response) frame:

```
+-------------------------------------------------------------------------------------------------------+
|  Length (1B)  |  Type (1B)  |  Company ID (2B)  |  Session ID (4B)  |  Window (4B)  |   HMAC Token (16B)  |
|     0x1A      |    0xFF     |      0x5050       |    Big-Endian     |  Big-Endian   |     ASCII Hex       |
+-------------------------------------------------------------------------------------------------------+
```

### Byte Fields Specification:
| Field | Offset | Length | Description |
| :--- | :--- | :--- | :--- |
| **AD Length** | `0` | 1 byte | `0x1A` (26 bytes following) |
| **AD Type** | `1` | 1 byte | `0xFF` (Manufacturer Specific Data) |
| **Company Identifier** | `2..3` | 2 bytes | `0x5050` (ASCII `'PP'` for ProxyProof) |
| **Session ID** | `4..7` | 4 bytes | Big-Endian `uint32` identifying the classroom attendance session |
| **Window Index** | `8..11` | 4 bytes | Big-Endian `uint32` discrete time-step index: $\lfloor \text{unix\_timestamp} / T \rfloor$ |
| **Cryptographic HMAC Token** | `12..27` | 16 bytes | Truncated HMAC-SHA256 signature in ASCII hex |

---

## 3. Cryptographic Token Rotation Algorithm

To defeat relay and replay attacks, the organizer generates a new high-entropy token every $T = 5$ seconds:

$$\text{Window Index } w = \left\lfloor \frac{\text{Current Epoch Time}}{T} \right\rfloor$$

$$\text{HMAC Digest} = \text{HMAC-SHA256}\Big(\text{SessionSecretKey},\; \text{"PROXYPROOF:"} \,\|\, \text{SessionID} \,\|\, w\Big)$$

$$\text{Token} = \text{HexEncode}(\text{HMAC Digest})[0 : 16]$$

### Window Skew & Grace Period
Mobile devices exhibit slight network latency and clock skew. The backend accommodates this with a configurable grace window $G = 1$:
- Valid windows: $\{w - 1, \; w, \; w + 1\}$
- Any token timestamped older than $(G + 1) \times T = 10\text{ seconds}$ is strictly discarded by the server.

---

## 4. Signal Propagation & Proximity Thresholding (RSSI)

Bluetooth Low Energy radio waves attenuate over distance following the log-distance path loss model:

$$\text{RSSI}(d) = \text{RSSI}(d_0) - 10 \cdot n \cdot \log_{10}\left(\frac{d}{d_0}\right) - X_\sigma$$

Where:
- $d$: distance between student and instructor beacon
- $d_0$: reference distance ($1\text{ meter}$, typical calibration $\approx -59\text{ dBm}$)
- $n$: path loss exponent ($2.0$ free space, $3.0\text{--}4.0$ indoor with concrete walls)
- $X_\sigma$: zero-mean Gaussian random variable representing wall shadow fading

### Empirical Classroom RSSI Boundaries:
- **Direct line-of-sight inside classroom (1--6m)**: $-50\text{ dBm}$ to $-72\text{ dBm}$
- **Perimeter classroom wall boundary (7--9m)**: $-73\text{ dBm}$ to $-75\text{ dBm}$
- **Hallway outside / Adjacent classroom (stray leakage)**: $-80\text{ dBm}$ to $-92\text{ dBm}$

**ProxyProof Default Filter**: Rejects any submission with $\text{RSSI} < -75\text{ dBm}$ (`PROXIMITY_RSSI_TOO_WEAK`).
