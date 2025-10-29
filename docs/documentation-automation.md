# Documentation Automation Setup

This guide covers setting up automated documentation generation, CI/CD pipelines, and maintenance workflows for the Rust PaddleOCR project.

## 🤖 Automated Documentation Generation

### Overview

The documentation automation system includes:
- **API Documentation**: Auto-generated from source code
- **Examples**: Verified and tested code examples
- **Performance Benchmarks**: Automated performance tracking
- **Quality Checks**: Documentation coverage and validation
- **Deployment**: Automatic publishing to documentation sites

---

## 📋 Table of Contents

- [CI/CD Pipeline Setup](#cicd-pipeline-setup)
- [Documentation Generation Scripts](#documentation-generation-scripts)
- [Quality Assurance](#quality-assurance)
- [Automated Testing](#automated-testing)
- [Deployment Configuration](#deployment-configuration)
- [Maintenance Workflows](#maintenance-workflows)

---

## 🚀 CI/CD Pipeline Setup

### GitHub Actions Workflow

Create `.github/workflows/docs.yml`:

```yaml
name: Documentation Generation and Deployment

on:
  push:
    branches: [main, develop]
    paths:
      - 'src/**'
      - 'docs/**'
      - 'Cargo.toml'
      - 'examples/**'
  pull_request:
    branches: [main]
    paths:
      - 'src/**'
      - 'docs/**'
      - 'Cargo.toml'
  schedule:
    # Run daily at 2 AM UTC
    - cron: '0 2 * * *'

env:
  CARGO_TERM_COLOR: always

jobs:
  # Generate and validate documentation
  generate-docs:
    name: Generate Documentation
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Install Rust toolchain
      uses: dtolnay/rust-toolchain@stable
      with:
        components: rustfmt, clippy

    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: |
          ~/.cargo/registry
          ~/.cargo/git
          target
        key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}

    - name: Install documentation dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y \
          python3-pip \
          python3-venv \
          graphviz \
          plantuml

    - name: Install Python tools
      run: |
        python3 -m pip install --upgrade pip
        pip3 install \
          mkdocs \
          mkdocs-material \
          mkdocs-mermaid2-plugin \
          mkdocs-git-revision-date-localized-plugin

    - name: Generate API documentation
      run: |
        cargo doc --no-deps --all-features
        cargo doc --no-deps --document-private-items

    - name: Run documentation generation script
      run: |
        chmod +x scripts/generate_docs.py
        ./scripts/generate_docs.py

    - name: Validate documentation
      run: |
        chmod +x scripts/validate_docs.sh
        ./scripts/validate_docs.sh

    - name: Check documentation coverage
      run: |
        chmod +x scripts/check_coverage.py
        ./scripts/check_coverage.py

    - name: Run examples
      run: |
        chmod +x scripts/test_examples.sh
        ./scripts/test_examples.sh

    - name: Upload documentation artifacts
      uses: actions/upload-artifact@v3
      with:
        name: documentation
        path: |
          target/doc/
          docs/_build/
          docs/generated/
        retention-days: 30

  # Deploy to GitHub Pages
  deploy-docs:
    name: Deploy Documentation
    runs-on: ubuntu-latest
    needs: generate-docs
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'

    permissions:
      contents: read
      pages: write
      id-token: write

    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Download documentation artifacts
      uses: actions/download-artifact@v3
      with:
        name: documentation
        path: artifacts/

    - name: Setup Pages
      uses: actions/configure-pages@v3

    - name: Build MkDocs site
      run: |
        pip3 install -r docs/requirements.txt
        mkdocs build --site-dir public

    - name: Upload artifact
      uses: actions/upload-pages-artifact@v2
      with:
        path: public

    - name: Deploy to GitHub Pages
      id: deployment
      uses: actions/deploy-pages@v2

  # Performance benchmarks
  benchmark:
    name: Performance Benchmarks
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule' || contains(github.event.head_commit.message, '[benchmark]')

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Install Rust toolchain
      uses: dtolnay/rust-toolchain@stable

    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: |
          ~/.cargo/registry
          ~/.cargo/git
          target
        key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}

    - name: Run benchmarks
      run: |
        cargo bench --all-features
        chmod +x scripts/benchmark_docs.py
        ./scripts/benchmark_docs.py

    - name: Update benchmark results
      run: |
        chmod +x scripts/update_benchmarks.py
        ./scripts/update_benchmarks.py

    - name: Commit benchmark updates
      if: github.ref == 'refs/heads/main'
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add docs/benchmarks/
        git commit -m "Update benchmark results [skip ci]" || exit 0
        git push
```

---

## 📜 Documentation Generation Scripts

### Python Documentation Generator

Create `scripts/generate_docs.py`:

```python
#!/usr/bin/env python3
"""
Automated documentation generation for Rust PaddleOCR
"""

import os
import sys
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional

class DocumentationGenerator:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.docs_dir = repo_root / "docs"
        self.src_dir = repo_root / "src"
        self.generated_dir = self.docs_dir / "generated"

        # Ensure directories exist
        self.generated_dir.mkdir(exist_ok=True)

    def generate_api_docs(self) -> None:
        """Generate API documentation from Rust source code"""
        print("🔧 Generating API documentation...")

        # Run cargo doc
        result = subprocess.run(
            ["cargo", "doc", "--no-deps", "--all-features"],
            cwd=self.repo_root,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"❌ Failed to generate API docs: {result.stderr}")
            sys.exit(1)

        # Copy generated docs
        api_src = self.repo_root / "target" / "doc"
        api_dst = self.generated_dir / "api"

        if api_src.exists():
            if api_dst.exists():
                import shutil
                shutil.rmtree(api_dst)
            shutil.copytree(api_src, api_dst)
            print("✅ API documentation generated")
        else:
            print("⚠️  API documentation not found")

    def extract_rust_docstrings(self) -> Dict[str, Dict]:
        """Extract docstrings from Rust source files"""
        print("📚 Extracting Rust docstrings...")

        docs = {}

        for rust_file in self.src_dir.rglob("*.rs"):
            if rust_file.name == "main.rs":
                continue

            module_docs = self._parse_rust_file(rust_file)
            if module_docs:
                docs[str(rust_file.relative_to(self.src_dir))] = module_docs

        return docs

    def _parse_rust_file(self, file_path: Path) -> Dict:
        """Parse a single Rust file for documentation"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            docs = {
                'file': str(file_path),
                'module_doc': self._extract_module_doc(content),
                'functions': self._extract_function_docs(content),
                'structs': self._extract_struct_docs(content),
                'enums': self._extract_enum_docs(content),
                'traits': self._extract_trait_docs(content),
            }

            return docs

        except Exception as e:
            print(f"⚠️  Error parsing {file_path}: {e}")
            return {}

    def _extract_module_doc(self, content: str) -> Optional[str]:
        """Extract module-level documentation"""
        match = re.search(r'//!\s*(.+?)(?=\n\n|\n//!|\npub|\n#)', content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _extract_function_docs(self, content: str) -> List[Dict]:
        """Extract function documentation"""
        functions = []

        # Match public functions with doc comments
        pattern = r'///\s*(.+?)(?=\n\s*///|\n\s*pub\s+fn|\n})\s*pub\s+fn\s+(\w+)\s*\([^)]*\)(?:\s*->\s*([^{]+))?'

        for match in re.finditer(pattern, content, re.DOTALL):
            doc = match.group(1).strip()
            name = match.group(2)
            return_type = match.group(3).strip() if match.group(3) else "()"  # Fixed here

            functions.append({
                'name': name,
                'documentation': doc,
                'return_type': return_type
            })

        return functions

    def _extract_struct_docs(self, content: str) -> List[Dict]:
        """Extract struct documentation"""
        structs = []

        pattern = r'///\s*(.+?)(?=\n\s*///|\n\s*pub\s+struct|\n})\s*pub\s+struct\s+(\w+)'

        for match in re.finditer(pattern, content, re.DOTALL):
            doc = match.group(1).strip()
            name = match.group(2)

            structs.append({
                'name': name,
                'documentation': doc
            })

        return structs

    def _extract_enum_docs(self, content: str) -> List[Dict]:
        """Extract enum documentation"""
        enums = []

        pattern = r'///\s*(.+?)(?=\n\s*///|\n\s*pub\s+enum|\n})\s*pub\s+enum\s+(\w+)'

        for match in re.finditer(pattern, content, re.DOTALL):
            doc = match.group(1).strip()
            name = match.group(2)

            enums.append({
                'name': name,
                'documentation': doc
            })

        return enums

    def _extract_trait_docs(self, content: str) -> List[Dict]:
        """Extract trait documentation"""
        traits = []

        pattern = r'///\s*(.+?)(?=\n\s*///|\n\s*pub\s+trait|\n})\s*pub\s+trait\s+(\w+)'

        for match in re.finditer(pattern, content, re.DOTALL):
            doc = match.group(1).strip()
            name = match.group(2)

            traits.append({
                'name': name,
                'documentation': doc
            })

        return traits

    def generate_examples_index(self) -> None:
        """Generate examples index from examples directory"""
        print("📝 Generating examples index...")

        examples_dir = self.repo_root / "examples"
        if not examples_dir.exists():
            print("⚠️  No examples directory found")
            return

        examples = []

        for example_file in examples_dir.glob("*.rs"):
            example_info = self._parse_example_file(example_file)
            if example_info:
                examples.append(example_info)

        # Generate examples index markdown
        examples_md = self._generate_examples_markdown(examples)

        with open(self.generated_dir / "examples_index.md", 'w') as f:
            f.write(examples_md)

        print(f"✅ Generated index for {len(examples)} examples")

    def _parse_example_file(self, file_path: Path) -> Optional[Dict]:
        """Parse an example file for metadata"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract title from first comment or function name
            title_match = re.search(r'//\s*(.+?)(?=\n|$)', content)
            title = title_match.group(1).strip() if title_match else file_path.stem

            # Extract main function documentation
            main_doc_match = re.search(r'///\s*(.+?)(?=\n\s*///|\n\s*fn\s+main)', content, re.DOTALL)
            description = main_doc_match.group(1).strip() if main_doc_match else ""

            return {
                'name': file_path.stem,
                'title': title,
                'description': description,
                'file': str(file_path.relative_to(self.repo_root)),
                'run_command': f"cargo run --example {file_path.stem}"
            }

        except Exception as e:
            print(f"⚠️  Error parsing example {file_path}: {e}")
            return None

    def _generate_examples_markdown(self, examples: List[Dict]) -> str:
        """Generate markdown for examples index"""
        md = """# Examples Index

This index is automatically generated from the examples directory.

## Available Examples

"""

        for example in sorted(examples, key=lambda x: x['name']):
            md += f"""### {example['title']}

**File:** `{example['file']}`
**Run:** `{example['run_command']}`

{example['description']}

```bash
{example['run_command']}
```

---

"""

        md += """*This index is automatically generated. Do not edit manually.*"""

        return md

    def generate_performance_report(self) -> None:
        """Generate performance documentation from benchmarks"""
        print("📊 Generating performance report...")

        # Run benchmarks
        result = subprocess.run(
            ["cargo", "bench", "--all-features"],
            cwd=self.repo_root,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"⚠️  Benchmarks failed: {result.stderr}")
            return

        # Parse benchmark results
        benchmark_data = self._parse_benchmark_output(result.stdout)

        # Generate performance report
        report = self._generate_performance_markdown(benchmark_data)

        with open(self.generated_dir / "performance_report.md", 'w') as f:
            f.write(report)

        print("✅ Performance report generated")

    def _parse_benchmark_output(self, output: str) -> Dict:
        """Parse cargo bench output"""
        benchmarks = {}

        # Simple regex to extract benchmark results
        pattern = r'test\s+(\w+)\s+\.\+\s+bench:\s+([\d,]+)\s+ns/iter'

        for match in re.finditer(pattern, output):
            name = match.group(1)
            time_ns = int(match.group(2).replace(',', ''))

            benchmarks[name] = {
                'time_ns': time_ns,
                'time_ms': time_ns / 1_000_000,
                'time_us': time_ns / 1_000
            }

        return benchmarks

    def _generate_performance_markdown(self, benchmarks: Dict) -> str:
        """Generate markdown for performance report"""
        md = """# Performance Report

This report is automatically generated from benchmark results.

## Benchmark Results

| Benchmark | Time (ns/iter) | Time (μs/iter) | Time (ms/iter) |
|-----------|----------------|----------------|----------------|
"""

        for name, data in sorted(benchmarks.items()):
            md += f"| {name} | {data['time_ns']:,} | {data['time_us']:.2f} | {data['time_ms']:.4f} |\n"

        md += f"""
## Summary

- **Total benchmarks run**: {len(benchmarks)}
- **Generated on**: {subprocess.check_output(['date']).decode().strip()}

*This report is automatically generated. Do not edit manually.*
"""

        return md

    def generate_changelog(self) -> None:
        """Generate changelog from git history"""
        print("📝 Generating changelog...")

        try:
            # Get recent commits
            result = subprocess.run(
                ["git", "log", "--oneline", "--decorate", "--graph", "-20"],
                cwd=self.repo_root,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                changelog = f"""# Recent Changes

This changelog is automatically generated from git history.

```
{result.stdout}
```

*Last updated: {subprocess.check_output(['date']).decode().strip()}*
"""

                with open(self.generated_dir / "changelog.md", 'w') as f:
                    f.write(changelog)

                print("✅ Changelog generated")
            else:
                print("⚠️  Failed to generate changelog")

        except Exception as e:
            print(f"⚠️  Error generating changelog: {e}")

    def run_all(self) -> None:
        """Run all documentation generation tasks"""
        print("🚀 Starting documentation generation...")

        self.generate_api_docs()
        self.generate_examples_index()
        self.generate_performance_report()
        self.generate_changelog()

        # Save metadata
        metadata = {
            'generated_at': subprocess.check_output(['date', '-Iseconds']).decode().strip(),
            'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip(),
            'rust_version': subprocess.check_output(['rustc', '--version']).decode().strip(),
        }

        with open(self.generated_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)

        print("✅ Documentation generation complete!")

def main():
    """Main entry point"""
    repo_root = Path(__file__).parent.parent

    generator = DocumentationGenerator(repo_root)
    generator.run_all()

if __name__ == "__main__":
    main()
```

### Documentation Validation Script

Create `scripts/validate_docs.sh`:

```bash
#!/bin/bash
set -e

echo "🔍 Validating documentation..."

# Check if all documented examples actually exist
echo "📝 Checking example references..."
find docs/ -name "*.md" -exec grep -l "cargo run --example" {} \; | while read file; do
    echo "  Checking $file..."
    grep -o "cargo run --example [a-zA-Z0-9_-]*" "$file" | while read cmd; do
        example=$(echo "$cmd" | cut -d' ' -f4)
        if [ ! -f "examples/$example.rs" ]; then
            echo "❌ Example $example.rs referenced in $file but does not exist"
            exit 1
        fi
    done
done

# Check if all code blocks are valid Rust
echo "🦀 Checking Rust code blocks..."
find docs/ -name "*.md" -exec grep -l "```rust" {} \; | while read file; do
    echo "  Checking $file..."

    # Extract rust code blocks
    awk '/```rust/,/```/' "$file" | sed '/```rust/d; /```/d' > /tmp/temp_code.rs

    # Try to compile (allowing for incomplete examples)
    if ! cargo check --quiet --bin temp 2>/dev/null && [ -s /tmp/temp_code.rs ]; then
        echo "⚠️  Code block in $file may have compilation issues"
    fi

    rm -f /tmp/temp_code.rs
done

# Check for broken internal links
echo "🔗 Checking internal links..."
find docs/ -name "*.md" -exec grep -H "\[.*\](.*.md)" {} \; | while read line; do
    link=$(echo "$line" | sed 's/.*\](.*\.md).*/\1/')
    file=$(echo "$line" | cut -d: -f1)

    if [[ "$link" == http* ]]; then
        continue  # Skip external links
    fi

    target="docs/$link"
    if [ ! -f "$target" ]; then
        echo "❌ Broken link in $file: $link"
        exit 1
    fi
done

# Check image references
echo "🖼️  Checking image references..."
find docs/ -name "*.md" -exec grep -H "!\[.*\](" {} \; | while read line; do
    img=$(echo "$line" | sed 's/.*!\[.*\](\([^)]*\)).*/\1/')
    file=$(echo "$line" | cut -d: -f1)

    if [[ "$img" == http* ]]; then
        continue  # Skip external images
    fi

    target="docs/$img"
    if [ ! -f "$target" ]; then
        echo "❌ Broken image reference in $file: $img"
        exit 1
    fi
done

# Check for required sections in main documentation
echo "📋 Checking required sections..."
required_files=(
    "docs/README.md"
    "docs/api-reference.md"
    "docs/examples.md"
    "docs/performance.md"
    "docs/architecture.md"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required documentation file missing: $file"
        exit 1
    fi
done

# Check README for quick start section
if ! grep -q "## Quick Start" docs/README.md; then
    echo "❌ README.md missing Quick Start section"
    exit 1
fi

# Check API reference for all public items
echo "🔍 Checking API reference completeness..."
public_items=$(cargo doc --no-deps --open 2>&1 | grep -c "found" || true)
echo "  Found $public_items documented items"

echo "✅ Documentation validation passed!"
```

### Coverage Check Script

Create `scripts/check_coverage.py`:

```python
#!/usr/bin/env python3
"""
Check documentation coverage for Rust PaddleOCR
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class DocumentationCoverage:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.src_dir = repo_root / "src"

    def check_coverage(self) -> Dict:
        """Check documentation coverage across the codebase"""
        results = {
            'total_functions': 0,
            'documented_functions': 0,
            'total_structs': 0,
            'documented_structs': 0,
            'total_enums': 0,
            'documented_enums': 0,
            'total_traits': 0,
            'documented_traits': 0,
            'missing_documentation': []
        }

        for rust_file in self.src_dir.rglob("*.rs"):
            if rust_file.name == "main.rs":
                continue

            file_results = self._check_file_coverage(rust_file)

            for key in ['total_functions', 'documented_functions',
                       'total_structs', 'documented_structs',
                       'total_enums', 'documented_enums',
                       'total_traits', 'documented_traits']:
                results[key] += file_results.get(key, 0)

            results['missing_documentation'].extend(file_results.get('missing_documentation', []))

        # Calculate percentages
        if results['total_functions'] > 0:
            results['function_coverage'] = (results['documented_functions'] / results['total_functions']) * 100
        else:
            results['function_coverage'] = 100

        if results['total_structs'] > 0:
            results['struct_coverage'] = (results['documented_structs'] / results['total_structs']) * 100
        else:
            results['struct_coverage'] = 100

        if results['total_enums'] > 0:
            results['enum_coverage'] = (results['documented_enums'] / results['total_enums']) * 100
        else:
            results['enum_coverage'] = 100

        if results['total_traits'] > 0:
            results['trait_coverage'] = (results['documented_traits'] / results['total_traits']) * 100
        else:
            results['trait_coverage'] = 100

        return results

    def _check_file_coverage(self, file_path: Path) -> Dict:
        """Check coverage for a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            results = {
                'total_functions': 0,
                'documented_functions': 0,
                'total_structs': 0,
                'documented_structs': 0,
                'total_enums': 0,
                'documented_enums': 0,
                'total_traits': 0,
                'documented_traits': 0,
                'missing_documentation': []
            }

            # This is a simplified check - in practice, you'd want more sophisticated parsing
            # For Rust, you might use syn crate or regex patterns

            # Check for public functions
            import re

            # Functions
            func_pattern = r'pub\s+fn\s+(\w+)'
            for match in re.finditer(func_pattern, content):
                results['total_functions'] += 1
                func_name = match.group(1)

                # Check if function has documentation
                if self._has_documentation(content, func_name, 'fn'):
                    results['documented_functions'] += 1
                else:
                    results['missing_documentation'].append({
                        'type': 'function',
                        'name': func_name,
                        'file': str(file_path.relative_to(self.src_dir))
                    })

            # Structs
            struct_pattern = r'pub\s+struct\s+(\w+)'
            for match in re.finditer(struct_pattern, content):
                results['total_structs'] += 1
                struct_name = match.group(1)

                if self._has_documentation(content, struct_name, 'struct'):
                    results['documented_structs'] += 1
                else:
                    results['missing_documentation'].append({
                        'type': 'struct',
                        'name': struct_name,
                        'file': str(file_path.relative_to(self.src_dir))
                    })

            # Enums
            enum_pattern = r'pub\s+enum\s+(\w+)'
            for match in re.finditer(enum_pattern, content):
                results['total_enums'] += 1
                enum_name = match.group(1)

                if self._has_documentation(content, enum_name, 'enum'):
                    results['documented_enums'] += 1
                else:
                    results['missing_documentation'].append({
                        'type': 'enum',
                        'name': enum_name,
                        'file': str(file_path.relative_to(self.src_dir))
                    })

            return results

        except Exception as e:
            print(f"Error checking {file_path}: {e}")
            return {}

    def _has_documentation(self, content: str, name: str, item_type: str) -> bool:
        """Check if an item has documentation"""
        import re

        # Look for doc comments before the item
        pattern = rf'(///.*\n)*\s*pub\s+{item_type}\s+{name}'
        match = re.search(pattern, content)

        if match:
            doc_text = match.group(0)
            return '///' in doc_text

        return False

    def print_coverage_report(self, results: Dict) -> None:
        """Print coverage report"""
        print("📊 Documentation Coverage Report")
        print("=" * 40)

        print(f"Functions: {results['documented_functions']}/{results['total_functions']} "
              f"({results.get('function_coverage', 0):.1f}%)")

        print(f"Structs: {results['documented_structs']}/{results['total_structs']} "
              f"({results.get('struct_coverage', 0):.1f}%)")

        print(f"Enums: {results['documented_enums']}/{results['total_enums']} "
              f"({results.get('enum_coverage', 0):.1f}%)")

        print(f"Traits: {results['documented_traits']}/{results['total_traits']} "
              f"({results.get('trait_coverage', 0):.1f}%)")

        if results['missing_documentation']:
            print(f"\n⚠️  Missing documentation ({len(results['missing_documentation'])} items):")
            for item in results['missing_documentation'][:10]:  # Show first 10
                print(f"  - {item['type']} {item['name']} in {item['file']}")

            if len(results['missing_documentation']) > 10:
                print(f"  ... and {len(results['missing_documentation']) - 10} more")

        # Check minimum coverage thresholds
        min_coverage = 80.0

        for item_type in ['function', 'struct', 'enum', 'trait']:
            coverage = results.get(f'{item_type}_coverage', 100)
            if coverage < min_coverage:
                print(f"\n❌ {item_type.title()} coverage ({coverage:.1f}%) below threshold ({min_coverage}%)")
                sys.exit(1)

        print(f"\n✅ All coverage checks passed!")

def main():
    """Main entry point"""
    repo_root = Path(__file__).parent.parent

    coverage_checker = DocumentationCoverage(repo_root)
    results = coverage_checker.check_coverage()
    coverage_checker.print_coverage_report(results)

if __name__ == "__main__":
    main()
```

---

## 🔍 Quality Assurance

### Documentation Linting

Create `.markdownlint.json`:

```json
{
  "default": true,
  "MD013": {
    "line_length": 120,
    "code_blocks": false,
    "tables": false
  },
  "MD033": {
    "allowed_elements": ["br", "sub", "sup", "kbd", "mark", "img", "a", "div", "span"]
  },
  "MD041": false,
  "MD034": false,
  "MD036": false
}
```

### Pre-commit Configuration

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
        files: docs/
      - id: end-of-file-fixer
        files: docs/
      - id: check-yaml
        files: docs/
      - id: check-added-large-files
        files: docs/
      - id: check-merge-conflict
        files: docs/

  - repo: https://github.com/igorshubovych/markdownlint-cli
    rev: v0.33.0
    hooks:
      - id: markdownlint
        files: docs/.*\.md$
        args: [--config=.markdownlint.json]

  - repo: local
    hooks:
      - id: rust-docs
        name: Check Rust documentation
        entry: cargo doc --no-deps --all-features --document-private-items
        language: system
        pass_filenames: false
        files: src/.*\.rs$

      - id: validate-docs
        name: Validate documentation
        entry: ./scripts/validate_docs.sh
        language: script
        pass_filenames: false
        files: docs/.*\.md$

      - id: check-coverage
        name: Check documentation coverage
        entry: python3 scripts/check_coverage.py
        language: system
        pass_filenames: false
        files: src/.*\.rs$
```

---

## 🚀 Deployment Configuration

### MkDocs Configuration

Create `mkdocs.yml`:

```yaml
site_name: Rust PaddleOCR Documentation
site_description: Comprehensive documentation for the Rust PaddleOCR library
site_author: Rust PaddleOCR Team
site_url: https://rust-paddle-ocr.github.io/

repo_name: zibo-chen/rust-paddle-ocr
repo_url: https://github.com/zibo-chen/rust-paddle-ocr

nav:
  - Home: README.md
  - Getting Started:
    - Quick Start: quick-start.md
    - Installation: installation.md
    - Basic Usage: basic-usage.md
  - API Documentation:
    - API Reference: api-reference.md
    - C API: c-api.md
  - Guides:
    - Architecture: architecture.md
    - Examples: examples.md
    - Interactive Examples: interactive-examples.md
    - Performance: performance.md
  - Advanced:
    - Code Explanation: code-explanation.md
    - Memory Management: memory.md
    - Thread Safety: thread-safety.md
    - Error Handling: error-handling.md
  - Development:
    - Contributing: contributing.md
    - Development Setup: development.md
    - Testing: testing.md
    - Documentation Automation: documentation-automation.md

theme:
  name: material
  language: en
  palette:
    - scheme: default
      primary: blue
      accent: orange
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: blue
      accent: orange
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  font:
    text: Roboto
    code: Roboto Mono
  features:
    - navigation.tabs
    - navigation.tabs.sticky
    - navigation.sections
    - navigation.expand
    - navigation.indexes
    - navigation.top
    - search.highlight
    - search.share
    - content.code.copy
    - content.code.annotate

plugins:
  - search:
      lang: en
  - git-revision-date-localized:
      type: datetime
      timezone: UTC
  - mermaid2:
      version: 10.6.1
  - macros

markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.highlight
  - pymdownx.inlinehilite
  - pymdownx.keys
  - pymdownx.mark
  - pymdownx.snippets
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.tasklist:
      custom_checkbox: true
  - tables
  - footnotes
  - attr_list
  - md_in_html
  - toc:
      permalink: true

extra:
  analytics:
    provider: google
    property: G-XXXXXXXXXX
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/zibo-chen/rust-paddle-ocr
    - icon: fontawesome/brands/docker
      link: https://hub.docker.com/r/rust-paddle-ocr
    - icon: fontawesome/solid/paper-plane
      link: mailto:contact@rust-paddle-ocr.com

extra_css:
  - stylesheets/extra.css

extra_javascript:
  - javascripts/extra.js
```

### Python Requirements

Create `docs/requirements.txt`:

```txt
mkdocs>=1.5.0
mkdocs-material>=9.0.0
mkdocs-mermaid2-plugin>=1.0.0
mkdocs-git-revision-date-localized-plugin>=1.0.0
mkdocs-macros-plugin>=1.0.0
pymdown-extensions>=10.0.0
```

---

## 🔧 Maintenance Workflows

### Weekly Documentation Update

Create `.github/workflows/weekly-update.yml`:

```yaml
name: Weekly Documentation Update

on:
  schedule:
    # Run every Monday at 9 AM UTC
    - cron: '0 9 * * 1'
  workflow_dispatch:

jobs:
  update-docs:
    name: Update Documentation
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      with:
        token: ${{ secrets.GITHUB_TOKEN }}

    - name: Install Rust toolchain
      uses: dtolnay/rust-toolchain@stable

    - name: Install Python tools
      run: |
        pip3 install -r docs/requirements.txt

    - name: Update API documentation
      run: |
        cargo doc --no-deps --all-features
        python3 scripts/generate_docs.py

    - name: Check for changes
      id: changes
      run: |
        if git diff --quiet docs/; then
          echo "changed=false" >> $GITHUB_OUTPUT
        else
          echo "changed=true" >> $GITHUB_OUTPUT
        fi

    - name: Commit and push changes
      if: steps.changes.outputs.changed == 'true'
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add docs/
        git commit -m "📚 Auto-update documentation [skip ci]"
        git push
```

### Documentation Health Check

Create `.github/workflows/health-check.yml`:

```yaml
name: Documentation Health Check

on:
  schedule:
    # Run daily at 3 AM UTC
    - cron: '0 3 * * *'
  workflow_dispatch:

jobs:
  health-check:
    name: Documentation Health Check
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Install Rust toolchain
      uses: dtolnay/rust-toolchain@stable

    - name: Install Python tools
      run: |
        pip3 install requests beautifulsoup4 markdown

    - name: Check external links
      run: |
        python3 scripts/check_links.py

    - name: Validate examples
      run: |
        chmod +x scripts/test_examples.sh
        ./scripts/test_examples.sh

    - name: Check documentation coverage
      run: |
        python3 scripts/check_coverage.py

    - name: Generate health report
      run: |
        python3 scripts/health_report.py > docs/generated/health_report.md

    - name: Create issue if problems found
      if: failure()
      uses: actions/github-script@v6
      with:
        script: |
          github.rest.issues.create({
            owner: context.repo.owner,
            repo: context.repo.repo,
            title: 'Documentation Health Check Failed',
            body: 'The automated documentation health check has failed. Please review the workflow logs and fix any issues.',
            labels: ['documentation', 'maintenance']
          })
```

---

## 📊 Monitoring and Analytics

### Documentation Metrics

Create `scripts/docs_metrics.py`:

```python
#!/usr/bin/env python3
"""
Generate documentation metrics and analytics
"""

import json
import os
from pathlib import Path
from datetime import datetime

def calculate_metrics(docs_dir: Path) -> dict:
    """Calculate documentation metrics"""
    metrics = {
        'total_files': 0,
        'total_lines': 0,
        'total_words': 0,
        'code_blocks': 0,
        'images': 0,
        'internal_links': 0,
        'external_links': 0,
        'tables': 0,
        'last_updated': datetime.now().isoformat()
    }

    for md_file in docs_dir.rglob("*.md"):
        if 'generated' in str(md_file):
            continue

        metrics['total_files'] += 1

        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

            metrics['total_lines'] += len(lines)
            metrics['total_words'] += len(content.split())

            # Count code blocks
            metrics['code_blocks'] += content.count('```')

            # Count images
            metrics['images'] += content.count('![')

            # Count links
            import re
            internal_links = len(re.findall(r'\[.*\]([^http].*\.md)', content))
            external_links = len(re.findall(r'\[.*\](http)', content))

            metrics['internal_links'] += internal_links
            metrics['external_links'] += external_links

            # Count tables
            metrics['tables'] += len(re.findall(r'\|.*\|', content))

    return metrics

def main():
    """Main entry point"""
    docs_dir = Path(__file__).parent.parent / "docs"

    metrics = calculate_metrics(docs_dir)

    # Save metrics
    metrics_file = docs_dir / "generated" / "metrics.json"
    metrics_file.parent.mkdir(exist_ok=True)

    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)

    # Print summary
    print("📊 Documentation Metrics:")
    print(f"  Files: {metrics['total_files']}")
    print(f"  Lines: {metrics['total_lines']}")
    print(f"  Words: {metrics['total_words']}")
    print(f"  Code blocks: {metrics['code_blocks']}")
    print(f"  Images: {metrics['images']}")
    print(f"  Internal links: {metrics['internal_links']}")
    print(f"  External links: {metrics['external_links']}")
    print(f"  Tables: {metrics['tables']}")

if __name__ == "__main__":
    main()
```

---

## 🎯 Best Practices

### Documentation Standards

1. **Code Examples**: All examples must be tested and working
2. **API Coverage**: All public APIs must be documented
3. **Version Sync**: Documentation must match code version
4. **Link Validation**: All links must be valid
5. **Image Optimization**: Images should be optimized for web

### Review Process

1. **Automated Checks**: CI/CD validates documentation quality
2. **Manual Review**: Technical accuracy reviewed by maintainers
3. **User Testing**: Examples tested by community members
4. **Accessibility**: Documentation tested for accessibility compliance

### Update Workflow

1. **Code Changes**: Trigger documentation updates
2. **Auto-Generation**: Scripts generate new documentation
3. **Validation**: Automated checks validate quality
4. **Review**: Manual review of significant changes
5. **Deployment**: Automatic deployment to documentation site

---

This comprehensive documentation automation setup ensures that the Rust PaddleOCR documentation stays current, accurate, and high-quality with minimal manual effort.