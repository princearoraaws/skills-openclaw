---
name: crypt
version: "1.0.0"
description: "Encrypt, decrypt, hash, and sign data using standard cryptographic algorithms. Use when you need data protection or integrity verification."
author: BytesAgain
homepage: https://bytesagain.com
source: https://github.com/bytesagain/ai-skills
tags: [cryptography, encryption, hashing, security, password, signing]
---

# Crypt — Encryption & Decryption Tool

Crypt is a command-line cryptography toolkit that provides encryption, decryption, hashing, digital signing, key generation, encoding/decoding, and password generation. It uses Python's built-in `hashlib`, `hmac`, and other standard library modules.

Operation history is stored in `~/.crypt/data.jsonl` (sensitive data like keys and plaintexts are NOT stored).

## Prerequisites

- Python 3.8+ with standard library
- `bash` shell

## Commands

### `encrypt`
Encrypt text or file content using AES-like XOR cipher or other algorithms.

**Environment Variables:**
- `INPUT` (required) — Text to encrypt, or file path if `IS_FILE=true`
- `KEY` (required) — Encryption key/passphrase
- `ALGORITHM` — Algorithm: `aes-xor`, `caesar`, `vigenere`, `xor` (default: aes-xor)
- `IS_FILE` — Set to `true` for file input (default: false)
- `OUTPUT` — Output file path (default: stdout)

**Example:**
```bash
INPUT="Hello World" KEY="mysecret" bash scripts/script.sh encrypt
```

### `decrypt`
Decrypt previously encrypted data.

**Environment Variables:**
- `INPUT` (required) — Encrypted text or file path
- `KEY` (required) — Decryption key/passphrase
- `ALGORITHM` — Algorithm used for encryption (default: aes-xor)
- `IS_FILE` — Set to `true` for file input (default: false)

### `hash`
Generate cryptographic hash of text or file.

**Environment Variables:**
- `INPUT` (required) — Text to hash, or file path if `IS_FILE=true`
- `ALGORITHM` — Hash algorithm: `md5`, `sha1`, `sha256`, `sha512`, `sha3_256` (default: sha256)
- `IS_FILE` — Set to `true` for file input (default: false)

**Example:**
```bash
INPUT="password123" ALGORITHM=sha256 bash scripts/script.sh hash
```

### `sign`
Create an HMAC signature for data integrity verification.

**Environment Variables:**
- `INPUT` (required) — Data to sign
- `KEY` (required) — Signing key
- `ALGORITHM` — Hash algorithm for HMAC (default: sha256)

### `verify`
Verify an HMAC signature against data.

**Environment Variables:**
- `INPUT` (required) — Original data
- `KEY` (required) — Signing key
- `SIGNATURE` (required) — Signature to verify
- `ALGORITHM` — Hash algorithm (default: sha256)

### `keygen`
Generate random keys or key pairs.

**Environment Variables:**
- `LENGTH` — Key length in bytes (default: 32)
- `FORMAT` — Output format: `hex`, `base64`, `raw` (default: hex)
- `TYPE` — Key type: `symmetric`, `pair` (default: symmetric)

### `encode`
Encode data using Base64, Base32, or hex encoding.

**Environment Variables:**
- `INPUT` (required) — Data to encode
- `ENCODING` — Encoding type: `base64`, `base32`, `hex`, `url` (default: base64)

### `decode`
Decode Base64, Base32, hex, or URL-encoded data.

**Environment Variables:**
- `INPUT` (required) — Data to decode
- `ENCODING` — Encoding type: `base64`, `base32`, `hex`, `url` (default: base64)

### `password`
Generate secure random passwords.

**Environment Variables:**
- `LENGTH` — Password length (default: 16)
- `COUNT` — Number of passwords to generate (default: 1)
- `CHARSET` — Character set: `all`, `alpha`, `alnum`, `hex`, `digits` (default: all)
- `EXCLUDE` — Characters to exclude

### `config`
View or update configuration settings.

**Environment Variables:**
- `KEY` — Configuration key
- `VALUE` — Configuration value

### `help`
Display usage information and available commands.

### `version`
Display the current version of the crypt tool.

## Data Storage

Operation logs are stored in `~/.crypt/data.jsonl`. Each record contains:
- `id` — Unique operation identifier
- `timestamp` — ISO 8601 time
- `operation` — Operation type (encrypt, hash, sign, etc.)
- `algorithm` — Algorithm used
- `input_length` — Length of input data (NOT the data itself)
- `output_preview` — First 32 chars of output (for hashes/encoded data only)

## Configuration

Config stored in `~/.crypt/config.json`:
- `default_hash` — Default hash algorithm (default: sha256)
- `default_encoding` — Default encoding (default: base64)
- `password_length` — Default password length (default: 16)
- `log_operations` — Whether to log operations (default: true)

---

Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
