# NVC

Status: **✅ both examples run in CI** (`.github/workflows/integration.yml`).

The same flow as the [GHDL examples](../ghdl), with [NVC](https://www.nickg.me.uk/nvc/).
Run them with `./run.sh` in the example's directory. NVC keeps its libraries in
the current directory, so the scripts work inside `build/`.

## Simple: [`simple/run.sh`](simple/run.sh)

```bash
ohsh -t ../../../projects/simple -o build accumulator
while IFS= read -r f; do nvc --std=2008 -a "$f"; done < build/work_vhdl.src
```

## Advanced: [`advanced/run.sh`](advanced/run.sh)

Each library is analyzed with `--work=<library>` in the order of
`libraries.src`, and `-L.` lets later libraries find the earlier ones:

```bash
ohsh -t ../../../projects/advanced -w dsp_lib -o build accumulator
while IFS= read -r lib; do
  while IFS= read -r f; do
    nvc --std=2008 -L. --work="$lib" -a "$f"
  done < "build/${lib}_vhdl.src"
done < build/libraries.src
```

## Requirements

NVC (not in the default Ubuntu repositories, CI installs it with the
[`nickg/setup-nvc`](https://github.com/marketplace/actions/setup-nvc) action).
Docs: <https://www.nickg.me.uk/nvc/manual.html>.
