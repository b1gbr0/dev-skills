# Field notes: RouterOS in live use

Lessons from operating a RouterOS gateway in production — a router reset and
rebuild, DHCP reservation moves, service hardening. Everything below was
reproduced on RouterOS **7.24.4** unless stated otherwise.

## Non-ASCII in an inline SSH command breaks parsing

A script sent as `ssh admin@router '<script>'` is executed inline, and non-ASCII
text does not survive the trip. Cyrillic inside `:put` comes back garbled — a
literal `=== итог ===` printed as `=== : ===` — and the parser then fails with
errors that point at perfectly balanced lines:

```text
syntax error (line 1 column 28)
expected closing brace (line 1 column 78)
```

Rule: **inline commands stay ASCII-only**. When non-ASCII output or text is
needed, put the script in a `.rsc` file and `/import` it — UTF-8 inside files is
handled correctly (comments and `:put` strings in a file are safe).

## Enum values: quote them to get the real error

```text
/ip cloud set ddns-enabled=no
# syntax error (line 1 column 28)          <- misleading, points at the value

/ip cloud set ddns-enabled="no"
# invalid value of ddns-enabled, must be either yes or auto   <- the truth
```

Two takeaways. First, quoting an enum value converts a useless `syntax error`
into a message naming the property and its allowed values. Second, the value set
is not necessarily what intuition suggests: on 7.24 `ddns-enabled` accepts only
`yes` or `auto`, so MikroTik Cloud DDNS cannot be switched off explicitly — the
effective state is read from `back-to-home-vpn` (`revoked-and-disabled`).

## `/ip service`: `find` also matches live connection rows

`/ip service` lists active connections as dynamic items that carry the same
`name` as the service they belong to, so a plain `find` returns more than the
configuration row:

```text
:put [:len [/ip service find where name="ssh"]]              # 2
:put [:len [/ip service find where name="ssh" dynamic=no]]   # 1
```

`set`/`disable`/`enable` against the dynamic item fails, and a loop that does not
filter it aborts halfway. Always filter `dynamic=no`:

```text
:foreach s in={"ftp";"telnet";"api";"api-ssl"} do={
    :local it [/ip service find where name=$s dynamic=no]
    :if ([:len $it] > 0) do={ /ip service set $it disabled=yes }
}
```

Same idea for hardening: keep `ssh`/`www`/`winbox` reachable only from the LAN
(`available-from` set to the local subnet, e.g. the defconf `192.168.88.0/24`)
and disable `btest` separately via `/tool bandwidth-server set enabled=no` — it
is a `/tool`, not an `/ip service` entry, so it survives a service sweep.

## A changed DHCP reservation does not move a running client

Rewriting a lease (`make-static` + `set address=`) changes the server's record,
but the client keeps using its old address. RouterOS does **not** NAK a client
that asks for an address the server no longer associates with it: the client
renews into the void and only moves when its lease expires (30m with the default
defconf pool). A fresh `renew` is therefore not a fix — the client is not stuck,
it is simply never told anything.

Forcing a fresh DISCOVER, per client type:

- **Linux + systemd-networkd**: `networkctl renew` and `networkctl reconfigure`
  both reuse the lease stored in `/run/systemd/netif/leases/<ifindex>`, so
  neither moves the address. Delete that file and restart the unit instead:

  ```text
  rm -f /run/systemd/netif/leases/$(cat /sys/class/net/<iface>/ifindex)
  systemctl restart systemd-networkd
  ```

- **macOS**: `sudo ipconfig set en0 DHCP`.
- **Devices you cannot reach** (NAS, printer, phones): they move at lease expiry
  on their own. Order the moves so a reserved address is never handed out while
  its previous holder is still using it, and expect clients to keep the old
  address for up to the full lease time.

## Reservation scripts must handle an existing dynamic lease

The common idempotency idiom silently does nothing when the client already holds
a dynamic lease from the pool — the reservation is never created, and everything
pointing at the expected address breaks (a route via the old IP, a netwatch probe,
a PBR address-list):

```text
# broken: covers only the "no lease yet" case
:if ([:len [find mac-address=$mac]] = 0) do={ add address=$addr ... }
```

The else-branch is the load-bearing half — it converts whatever lease exists:

```text
:local l [find mac-address=$mac]
:if ([:len $l] = 0) do={
    add address=$addr mac-address=$mac server=defconf comment=$name
} else={
    :do { make-static $l } on-error={}
    set $l address=$addr server=defconf comment=$name
}
```

Verify the outcome, not the intent: after applying, check that the lease shows up
as **non-dynamic** (`/ip dhcp-server lease print where !dynamic`) with the
expected address — a silent skip looks exactly like success in the script output.
