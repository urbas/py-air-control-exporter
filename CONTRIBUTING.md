# Contributing to py-air-control-exporter

## Development Setup

1. Install the nix package manager:
   https://nixos.org/manual/nix/stable/installation/installation.html

2. Install direnv: https://direnv.net/

3. Run:

   ```bash
   export DEV_INSTALL_EDITABLE=true
   direnv allow
   ```

This will prepare all dependencies and install this package in editable mode.
You can start developing now.

```bash
# Run the main entry point of this project:
py-air-control-exporter --help

# Run tests
pytest py_air_control_exporter test

# Format, lint, and type-check the code:
ruff format
ruff check
pyright
```

## Release Process

1. **Update Version**

   - Edit `pyproject.toml` and update the `version` field
   - The version should follow [semantic versioning](https://semver.org/)

2. **Update Changelog**

   - Add a new section at the top of `CHANGELOG.md`
   - Use the new version number as the section header
   - List all notable changes under the new section

3. **Build Package**

   ```bash
   # Clean previous builds
   rm -rf dist/

   # Build the package
   hatchling build
   ```

4. **Upload to PyPI**

   ```bash
   # Upload to PyPI (requires PyPI credentials; username: __token__; pwd: <the token>)
   twine upload dist/*
   ```

5. **Create GitHub Release**
   - Create and push a new tag:
     ```bash
     git tag -a v$(hatchling version) -m "Release $(hatchling version)"
     git push origin v$(hatchling version)
     ```
   - Go to GitHub releases page
   - Create a new release using this tag
   - The package will be automatically published to PyPI via GitHub Actions
