# TidyID

[![PyPI version](https://img.shields.io/pypi/v/tidyid.svg)](https://pypi.org/project/tidyid/)
[![Python](https://img.shields.io/pypi/pyversions/tidyid.svg)](https://pypi.org/project/tidyid/)
[![Typing](https://img.shields.io/badge/typing-typed-3776AB.svg?logo=python&logoColor=white)](https://typing.python.org/)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/sheldonix/tidyid-python/blob/main/LICENSE)

A tiny, secure, and human-friendly ID generator for Python.

- **Tiny** A focused pure-Python package with zero runtime dependencies.
- **Secure** Uses the platform CSPRNG with unbiased sampling and no weak fallback. Generate independently across threads and processes; enforce absolute uniqueness with a database constraint.
- **Human-friendly** Creates letter-first, lowercase-alphanumeric IDs by default with a fixed `LLD` rhythm—no accidental long words, punctuation, or ambiguous characters. Easy to read, type, and transcribe; ready for URLs, filenames, database/cache/object-storage keys, HTML/CSS IDs, command lines, logs, and more.

```python
from tidyid import tidyid

id_1 = tidyid(32)  # qr9vc2xh8cq2ck3dr8jy7pa6zf9gd2bv (length = 32)
id_2 = tidyid(16)  # bg9ad6rm8vf5pf4t (length = 16)
id_3 = tidyid(10)  # kp8kb3mb9z (length = 10)
id_4 = tidyid(10, True)  # yb5kT4FR7z (length = 10, allow_uppercase = True)
```

Explicitly passing the length in application code is strongly recommended, even when using the default of 32.

## Install

```sh
pip install tidyid
```

**or**

```sh
uv add tidyid
```

## CLI

Install TidyID, then generate IDs:

```sh
tidyid
# tm4wa4hd4tz7qr9ke3qc5pt4xc4ay6tt (length = 32)

tidyid -s 16
# xk6fc7hb5ma2ac5x (length = 16)

tidyid -s 10 -u
# tH3Fg8Ev7t (length = 10, allow_uppercase = True)
```

Use `--size` or `-s` to set the length. Use `--allow-uppercase` or `-u`
to allow uppercase letters.

## Format

By default, IDs repeat two lowercase letters followed by one digit (`LLD`):

```text
cv4 hj7 hm5
```

| Characters | Positions | Alphabet |
| --- | --- | --- |
| Letters | First two of each group | `abcdefghjkmnpqrtuvwxyz` |
| Digits | Every third character | `23456789` |

- Every ID starts with a letter.
- `i`, `l`, `o`, `s`, `0`, and `1` are excluded to reduce visual and handwritten ambiguity.
- The pattern prevents long letter sequences and needs no escaping in URL paths, filenames, or HTML/CSS IDs.
- In default mode, typing needs no Shift key, `_`, `-`, or other punctuation.

`allow_uppercase` defaults to `False`. Set it to `True` to sample letter
positions from the combined uppercase and lowercase alphabet.

## API

| API | Description |
| --- | --- |
| `tidyid(length=32, allow_uppercase=False)` | Generate a 3–256 character ID; defaults to 32. |
| `is_valid_id(value, length=None, allow_uppercase=False)` | Check format and optional exact length. |
| `ensure_valid_id(value, length=None, allow_uppercase=False)` | Raise `InvalidIdLengthError` or `InvalidIdFormatError`. |
| `get_id_capacity(length=32, allow_uppercase=False)` | Return the exact ID space as an arbitrary-precision `int`. |
| `get_id_entropy(length=32, allow_uppercase=False)` | Return entropy in bits. |

Constants: `LETTERS`, `LETTERS_WITH_UPPERCASE`, `DIGITS`, `DEFAULT_LENGTH`, `MIN_LENGTH`, `MAX_LENGTH`.

Errors: `InvalidIdLengthError`, `InvalidIdFormatError`.

## Security

- **Unpredictability** Every call reads fresh bytes from Python's `os.urandom`, which uses the operating system's cryptographically secure random source. No random-byte pool or generated-ID pool is retained.
- **Uniformity** Letter positions use rejection sampling, while digit positions use an exact eight-way mapping. Both avoid modulo bias, so every valid ID of the same length and mode has equal probability.
- **Concurrency** Calls share no mutable generator state and are safe across threads and processes. On standard GIL-enabled CPython builds, use multiple processes when parallel generation throughput is required.
- **Collision-aware** Choose a length for your scale to make collisions extremely unlikely. Use a database `PRIMARY KEY` or `UNIQUE` constraint when absolute uniqueness must be enforced.

  > **Default mode (`allow_uppercase = False`)**
  >
  > | Length | Capacity | Entropy |
  > | ---: | ---: | ---: |
  > | 8 | 7,256,313,856 | 32.76 bits |
  > | 10 | 1,277,111,238,656 | 40.22 bits |
  > | 12 | 224,771,578,003,456 | 47.68 bits |
  > | 16 | 19,146,942,100,646,395,904 | 64.05 bits |
  > | 23 | 6,315,282,784,770,463,143,393,492,992 | 92.35 bits |
  > | 32 | 366,605,391,805,505,419,895,548,144,464,707,977,216 | 128.11 bits |

  > **Uppercase allowed (`allow_uppercase = True`)**
  >
  > | Length | Capacity | Entropy |
  > | ---: | ---: | ---: |
  > | 8 | 464,404,086,784 | 38.76 bits |
  > | 10 | 163,470,238,547,968 | 47.22 bits |
  > | 12 | 57,541,523,968,884,736 | 55.68 bits |
  > | 16 | 39,212,937,422,123,818,811,392 | 75.05 bits |
  > | 23 | 413,878,372,582,717,072,565,435,956,723,712 | 108.35 bits |
  > | 32 | 1,537,654,461,271,398,604,689,577,164,520,902,527,668,977,664 | 150.11 bits |

  Use 16 or more characters for large public datasets. For security tokens, choose the length based on your threat model. A 32-character TidyID provides 128.11 bits of entropy by default, or 150.11 bits with `allow_uppercase = True`.

## Database uniqueness

Use a primary key or unique constraint. Insert first and retry only an ID conflict—never query before inserting:

```python
for _ in range(128):
    identifier = tidyid(16)
    row = db.execute(
        """INSERT INTO resources (id) VALUES (%s)
           ON CONFLICT (id) DO NOTHING RETURNING id""",
        (identifier,),
    ).fetchone()
    if row is not None:
        return identifier
raise RuntimeError("unable to insert a resource with a unique TidyID")
```

Propagate network, permission, transaction, and non-ID constraint errors.

## Requirements

- Python `>=3.9`

## License

MIT
