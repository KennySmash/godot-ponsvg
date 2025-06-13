# Working with LunaSVG Submodule

## Overview

The LunaSVG library is included as a Git submodule, which provides better dependency management and makes it easier to update to newer versions.

## Submodule Information

- **Repository**: https://github.com/sammycage/lunasvg.git
- **Path**: `modules/ponsvg/src/lunasvg`
- **Current Version**: v3.3.0 (commit: 3166ff3)

## Working with the Submodule

### Initial Setup (for new clones)

When someone clones this repository, they need to initialize the submodule:

```bash
git clone <this-repo-url>
cd gotot-svg-module
git submodule update --init --recursive
```

Or clone with submodules in one command:

```bash
git clone --recursive <this-repo-url>
```

### Updating LunaSVG

To update to the latest version of LunaSVG:

```bash
cd modules/ponsvg/src/lunasvg
git fetch origin
git checkout master  # or specific tag/commit
cd ../../../..
git add modules/ponsvg/src/lunasvg
git commit -m "Update LunaSVG to <version>"
```

### Checking Submodule Status

```bash
git submodule status
```

### Pulling Changes (for contributors)

When pulling changes that include submodule updates:

```bash
git pull
git submodule update --recursive
```

## Development Notes

- The submodule is pinned to a specific commit for stability
- All LunaSVG source files are available in `modules/ponsvg/src/lunasvg/source/`
- Headers are in `modules/ponsvg/src/lunasvg/include/`
- PlutoVG (rendering backend) is in `modules/ponsvg/src/lunasvg/plutovg/`

## Build Integration

The SCons build system automatically includes the submodule sources. No additional configuration is needed for building.

## Benefits of Using Submodules

1. **Version Control**: Exact version tracking and reproducible builds
2. **Easy Updates**: Simple process to update to newer LunaSVG versions
3. **Space Efficient**: Only one copy of LunaSVG across all branches
4. **Upstream Tracking**: Easy to see what version we're using and update from upstream
5. **Clean History**: LunaSVG changes don't clutter our repository history
