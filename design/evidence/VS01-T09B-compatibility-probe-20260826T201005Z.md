# VS01-T09B compatibility probe

Timestamp: `2026-08-26T20:10:05Z`

Disposition: **PASS**

## Exact toolchain

- Node `24.20.0` (current active LTS, Krypton)
- pnpm `11.24.0`
- Python target `3.12.*`; compatibility execution used CPython `3.12.12`
- Playwright `1.62.1`, Chromium revision `1234`, Chrome for Testing `151.0.7922.34`

## Exact direct dependencies

Python runtime (2): `fastapi==0.141.1`, `uvicorn==0.52.4`.

Web runtime (3): `react@18.3.1`, `react-dom@18.3.1`, `ajv@8.20.0`.

Web development (12): `@axe-core/playwright@4.13.0`, `@biomejs/biome@2.5.10`, `@playwright/test@1.62.1`, `@testing-library/react@14.3.1`, `@types/node@24.13.3`, `@types/react@18.3.31`, `@types/react-dom@18.3.7`, `@vitejs/plugin-react@6.1.0`, `jsdom@30.0.1`, `typescript@5.9.3`, `vite@8.2.2`, `vitest@4.1.11`.

Total new direct dependencies: 17. Every version is exact. No forbidden family appeared.

## Compatibility result

- Node `24.20.0` satisfies the engines declared by Vite, plugin-react, Vitest, jsdom, Playwright, and pnpm.
- React/React DOM `18.3.1` satisfy the selected Testing Library and React type peer contracts.
- Vite `8.2.2` satisfies the selected plugin-react and Vitest peer ranges.
- FastAPI `0.141.1` and Uvicorn `0.52.4` lock and import with the existing Pydantic `2.13.4`; the resolved ASGI layer is Starlette `1.6.0`.
- Strict-peer npm installation, frozen npm installation, exact Python lock generation, frozen Python installation, and imports all passed.
- Exact-version `pnpm-lock.yaml` and `uv.lock` files can be produced.

## Probe commands and results

| Probe | Exit |
|---|---:|
| Official Node, PyPI, npm, and GitHub Action tag metadata queries | 0 |
| Exact pnpm runtime/development install with strict peer dependencies | 0 |
| `pnpm install --frozen-lockfile --strict-peer-dependencies` | 0 |
| `pnpm exec playwright install chromium` | 0 |
| Exact FastAPI/Uvicorn add and `uv lock --check` | 0 |
| Frozen Python sync without project install and exact imports | 0 |

Two initial read-only command-shape checks were corrected inside this single bounded probe: unsupported `uv add --exact` exited 2 before `uv add package==version` was used, and a non-exported `playwright-core/browsers.json` resolution attempt exited 1 before the installed package path was inspected directly. Neither changed the frozen dependency set.

## Workflow action pins

- `actions/checkout@11d5960a326750d5838078e36cf38b85af677262`
- `actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065`
- `actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020`
- `astral-sh/setup-uv@d0cc045d04ccac9d8b7881df0226f9e82c39688e`

Network use was limited to official package/toolchain metadata and downloads, exact action repositories, and the official Playwright browser download. Product runtime traffic was zero.
