# Package Mirrors (Liara)

To avoid unstable connections to the default registries, this project is
configured to install dependencies from Liara's Iranian mirrors. The frontend
and backend already pick these up automatically via committed config files.

| Ecosystem | Mirror URL |
| --------- | ---------- |
| npm       | `https://package-mirror.liara.ir/repository/npm/` |
| PyPI      | `https://package-mirror.liara.ir/repository/pypi/simple/` |
| Docker    | `https://docker-mirror.liara.ir` |
| Debian    | `http://linux-mirror.liara.ir/repository/debian/` |
| Debian security | `http://linux-mirror.liara.ir/repository/debian-security/` |

---

## npm (frontend) — already configured

`frontend/.npmrc` sets the registry, so `npm install` in `frontend/` just works:

```ini
registry=https://package-mirror.liara.ir/repository/npm/
```

> Verified: `npm install` completes against this mirror.

---

## PyPI (backend) — already configured

`backend/pip.ini` points pip at the mirror. Activate it for your shell:

```powershell
cd backend
$env:PIP_CONFIG_FILE = "$PWD\pip.ini"
python -m pip install -r requirements.txt
```

…or pass it inline once:

```powershell
python -m pip install -r requirements.txt -i https://package-mirror.liara.ir/repository/pypi/simple/ --trusted-host package-mirror.liara.ir
```

> Verified: package downloads succeed against this mirror.

---

## Docker (for future deployment)

Add the registry mirror to the Docker daemon config
(`%ProgramData%\docker\config\daemon.json` on Windows, `/etc/docker/daemon.json`
on Linux), then restart Docker:

```json
{
  "registry-mirrors": ["https://docker-mirror.liara.ir"]
}
```

A ready-made copy lives at `docs/docker-daemon.json`.

---

## Debian / apt (for future Linux deployment)

Replace the contents of `/etc/apt/sources.list` (Debian 12 "bookworm" example):

```
deb http://linux-mirror.liara.ir/repository/debian/ bookworm main contrib non-free non-free-firmware
deb http://linux-mirror.liara.ir/repository/debian/ bookworm-updates main contrib non-free non-free-firmware
deb http://linux-mirror.liara.ir/repository/debian-security/ bookworm-security main contrib non-free non-free-firmware
```

Then `apt update`. A ready-made copy lives at `docs/debian.sources.list`.
