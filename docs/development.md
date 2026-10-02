# Development

```bash
git clone https://github.com/logvik-org/oshsh.git
cd oshsh
source scripts/setup-dev.sh   # create .venv, install everything, activate it
make test                     # run tests with coverage
make lint                     # run every pre-commit check
make examples                 # run the integration examples, as CI does
```

See [CONTRIBUTING.md](https://github.com/logvik-org/oshsh/blob/main/CONTRIBUTING.md) for details.
