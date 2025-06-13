# PonSVG Module Testing Guide

This directory contains all testing utilities and assets for the PonSVG module.

## Directory Structure

```
tests/
├── assets/               # Test SVG files and resources
│   ├── test_complex.svg  # Complex SVG with symbols and styling
│   └── test_svg.svg      # Simple test SVG
├── output/               # Test output files (generated)
├── test_runner.py        # Main test runner with dev environment integration
├── build_test.py         # Build validation tests
├── test_module.py        # Basic functionality tests (GDScript)
├── test_advanced.py      # Advanced feature tests (GDScript)
├── test_enhanced.py      # Performance and caching tests (GDScript)
└── README.md            # This file
```

## Configuration

The test runner uses `dev-settings.json` in the project root to configure the development environment:

```json
{
  "godot_dev_path": "E:\\Dev\\godot-dev",
  "module_name": "ponsvg",
  "build_target": "editor",
  "platform": "windows"
}
```

Update this file with your local Godot development path.

## Running Tests

### Build Validation

Test that the module can be built properly:

```bash
python tests/test_runner.py test
```

### Development Workflow

1. **Check Status**: See current environment status
   ```bash
   python tests/test_runner.py status
   ```

2. **Deploy Module**: Copy module to Godot and optionally build
   ```bash
   python tests/test_runner.py deploy
   ```

3. **Full Cycle**: Copy, build, and test
   ```bash
   python tests/test_runner.py all
   ```

### Individual Commands

- `python tests/test_runner.py copy` - Copy module to Godot directory
- `python tests/test_runner.py build` - Build Godot with PonSVG module
- `python tests/test_runner.py test` - Run build validation tests

## GDScript Tests

The following test files contain GDScript code to run in Godot once the module is compiled:

### test_module.py
Basic functionality testing:
- SVG loading from string
- Basic rasterization
- Texture and sprite creation

### test_advanced.py
Advanced feature testing:
- Symbol extraction and rendering
- Style overrides (fill, stroke)
- Runtime style modifications
- Multiple sprite instances

### test_enhanced.py
Performance and optimization testing:
- Caching system validation
- LOD (Level of Detail) system
- Performance benchmarking
- Memory usage optimization

## Test Assets

### test_svg.svg
Simple SVG with:
- Basic shapes (rectangle, circle)
- Symbol definitions
- Text elements

### test_complex.svg
Complex SVG with:
- Multiple symbols with IDs
- Various shapes and paths
- Styling attributes
- Use elements for testing symbol instantiation

## Expected Test Results

When running the complete test suite, you should see:

✅ Module structure validation
✅ LunaSVG library integration
✅ Build system configuration
✅ Basic SVG loading and parsing
✅ Symbol extraction and identification
✅ Style override functionality
✅ Rasterization at multiple sizes
✅ Caching system performance
✅ LOD system optimization

## Troubleshooting

### Common Issues

1. **"Godot path not found"**
   - Update `godot_dev_path` in `dev-settings.json`
   - Ensure the path points to a valid Godot source directory

2. **"Build failed"**
   - Check that all LunaSVG files are present
   - Verify scons is installed and accessible
   - Check compiler prerequisites for your platform

3. **"Module not found in Godot"**
   - Run `python tests/test_runner.py copy` to install the module
   - Verify the module appears in `godot-dev/modules/ponsvg/`

4. **GDScript tests fail**
   - Ensure you're running tests in a Godot build that includes the PonSVG module
   - Check that test assets are accessible to your Godot project
   - Verify the module is properly registered (check Editor -> Project Settings -> Plugins)

### Debug Information

The test runner provides detailed status information:

```bash
python tests/test_runner.py status
```

This shows:
- Project and Godot paths
- Module installation status
- Available test assets
- Build configuration

## Contributing Tests

When adding new tests:

1. Place GDScript test code in a new `test_*.py` file
2. Add test assets to `tests/assets/`
3. Update this README with test descriptions
4. Ensure tests can run independently
5. Add validation for expected results

## Performance Benchmarks

The enhanced test suite includes performance benchmarks for:

- **Parsing**: SVG document parsing time
- **Rasterization**: Image generation speed at various sizes
- **Caching**: Cache hit/miss ratios and performance impact
- **Memory**: Memory usage patterns
- **LOD**: Level-of-detail performance benefits

Results help validate that optimizations are working correctly and identify performance regressions.
