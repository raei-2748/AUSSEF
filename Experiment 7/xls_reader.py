"""Minimal reader for legacy Excel .xls (OLE2 compound file + BIFF8) workbooks.
Only what is needed for the ABS CABEE data cubes: sheet names, numbers (NUMBER/RK/MULRK/FORMULA numeric
results) and strings (LABELSST/LABEL). Written because xlrd is not installed. Returns {sheet: {(row, col): value}}."""
import struct


def _ole_stream(path, want='Workbook'):
    data = open(path, 'rb').read()
    assert data[:8] == bytes.fromhex('D0CF11E0A1B11AE1'), 'not an OLE2 file'
    sec_shift = struct.unpack_from('<H', data, 30)[0]
    ssz = 1 << sec_shift
    n_fat, first_dir, _, mini_cut, first_mini_fat, n_mini_fat, first_difat, n_difat = \
        struct.unpack_from('<IIIIIIII', data, 44)
    sec = lambda i: data[(i + 1) * ssz:(i + 2) * ssz]
    difat = list(struct.unpack_from('<109I', data, 76))
    nxt = first_difat
    for _ in range(n_difat):
        s = sec(nxt)
        vals = struct.unpack_from(f'<{ssz // 4}I', s)
        difat += vals[:-1]
        nxt = vals[-1]
    fat = []
    for i in difat[:n_fat]:
        fat += struct.unpack_from(f'<{ssz // 4}I', sec(i))

    def chain(start):
        out, i = [], start
        while i < 0xFFFFFFFA:
            out.append(i)
            i = fat[i]
        return out

    d = b''.join(sec(i) for i in chain(first_dir))
    for k in range(len(d) // 128):
        e = d[k * 128:(k + 1) * 128]
        nlen = struct.unpack_from('<H', e, 64)[0]
        name = e[:max(nlen - 2, 0)].decode('utf-16-le')
        if name in (want, 'Book'):
            start, size = struct.unpack_from('<II', e, 116)
            assert size >= mini_cut, 'mini-stream workbooks not supported'
            return b''.join(sec(i) for i in chain(start))[:size]
    raise KeyError(want)


def _rk(v):
    if v & 2:
        x = float(v >> 2 if not (v & 0x80000000) else (v >> 2) - (1 << 30))
    else:
        x = struct.unpack('<d', struct.pack('<Q', (v & 0xFFFFFFFC) << 32))[0]
    return x / 100 if v & 1 else x


def _records(wb):
    p = 0
    while p + 4 <= len(wb):
        rid, ln = struct.unpack_from('<HH', wb, p)
        yield p, rid, wb[p + 4:p + 4 + ln]
        p += 4 + ln


def _read_sst(parts, total):
    """parts: list of byte chunks (SST body then CONTINUE bodies)."""
    out = []
    pi, buf, pos = 0, parts[0], 8

    def need(n):
        nonlocal pi, buf, pos
        if pos + n <= len(buf):
            return
        raise IndexError

    def take(n):
        nonlocal pi, buf, pos
        res = b''
        while n > 0:
            if pos >= len(buf):
                pi += 1; buf = parts[pi]; pos = 0
            k = min(n, len(buf) - pos)
            res += buf[pos:pos + k]; pos += k; n -= k
        return res

    for _ in range(total):
        if pos >= len(buf):
            pi += 1; buf = parts[pi]; pos = 0
        nch = struct.unpack('<H', take(2))[0]
        flags = take(1)[0]
        rt = struct.unpack('<H', take(2))[0] if flags & 8 else 0
        sz = struct.unpack('<I', take(4))[0] if flags & 4 else 0
        chars, wide = [], flags & 1
        remaining = nch
        while remaining > 0:
            if pos >= len(buf):
                pi += 1; buf = parts[pi]; pos = 0
                wide = buf[0] & 1; pos = 1          # each CONTINUE restates the char width
            avail = (len(buf) - pos) // (2 if wide else 1)
            k = min(remaining, avail)
            raw = buf[pos:pos + k * (2 if wide else 1)]
            pos += len(raw)
            chars.append(raw.decode('utf-16-le') if wide else raw.decode('latin-1'))
            remaining -= k
        take(4 * rt + sz)
        out.append(''.join(chars))
    return out


def read_xls(path, sheets=None):
    wb = _ole_stream(path)
    recs = list(_records(wb))
    bound, sst = [], []
    for i, (p, rid, body) in enumerate(recs):
        if rid == 0x85:
            off = struct.unpack_from('<I', body, 0)[0]
            nlen, flag = body[6], body[7]
            name = body[8:8 + nlen * 2].decode('utf-16-le') if flag & 1 else body[8:8 + nlen].decode('latin-1')
            bound.append((name, off))
        elif rid == 0xFC:
            parts = [body]
            j = i + 1
            while recs[j][1] == 0x3C:
                parts.append(recs[j][2]); j += 1
            sst = _read_sst(parts, struct.unpack_from('<I', body, 4)[0])
    pos_index = {p: k for k, (p, _, _) in enumerate(recs)}
    out = {}
    for name, off in bound:
        if sheets is not None and name not in sheets:
            continue
        cells = {}
        k = pos_index[off] + 1
        while recs[k][1] != 0x0A:
            _, rid, b = recs[k]
            if rid == 0x203:
                r, c = struct.unpack_from('<HH', b); cells[(r, c)] = struct.unpack_from('<d', b, 6)[0]
            elif rid == 0x27E:
                r, c = struct.unpack_from('<HH', b); cells[(r, c)] = _rk(struct.unpack_from('<I', b, 6)[0])
            elif rid == 0xBD:
                r, c0 = struct.unpack_from('<HH', b)
                n = (len(b) - 6) // 6
                for j in range(n):
                    cells[(r, c0 + j)] = _rk(struct.unpack_from('<I', b, 4 + 6 * j + 2)[0])
            elif rid == 0xFD:
                r, c, _, isst = struct.unpack_from('<HHHI', b); cells[(r, c)] = sst[isst]
            elif rid == 0x204:
                r, c, _, n = struct.unpack_from('<HHHH', b)
                flag = b[8]
                cells[(r, c)] = b[9:9 + 2 * n].decode('utf-16-le') if flag & 1 else b[9:9 + n].decode('latin-1')
            elif rid == 0x06:
                r, c = struct.unpack_from('<HH', b)
                if b[12:14] != b'\xff\xff':
                    cells[(r, c)] = struct.unpack_from('<d', b, 6)[0]
            k += 1
        out[name] = cells
    return out


def to_rows(cells):
    if not cells:
        return []
    nr = max(r for r, _ in cells) + 1
    nc = max(c for _, c in cells) + 1
    rows = [[None] * nc for _ in range(nr)]
    for (r, c), v in cells.items():
        rows[r][c] = v
    return rows
