#!/usr/bin/env python3
"""
Skill Finalizer - Validates and packages a customized skill with timestamp

This script is the final step in the customization workflow. It:
1. Confirms the user is ready to finalize
2. Validates the skill structure
3. Packages the skill with a timestamped filename for distribution

Usage:
    finalize_skill.py <skill-directory> [--output <output-directory>]

Examples:
    finalize_skill.py ./my-pdf-workflow
    finalize_skill.py ./my-pdf-workflow --output ~/Desktop
    finalize_skill.py ../custom-skills/my-design --output ./dist

The script creates a zip file with format: {skill-name}-{YYYYMMDD-HHMMSS}.zip
This allows users to track different versions of their customized skills.
"""

import sys
import zipfile
from pathlib import Path
from datetime import datetime


def validate_skill(skill_path):
    """
    Basic validation of a skill structure.

    Args:
        skill_path: Path to skill directory

    Returns:
        (is_valid, message) tuple
    """
    skill_path = Path(skill_path)

    # Check directory exists
    if not skill_path.exists():
        return False, f"Skill directory not found: {skill_path}"

    if not skill_path.is_dir():
        return False, f"Path is not a directory: {skill_path}"

    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found in skill directory"

    # Read and validate frontmatter
    import re
    content = skill_md.read_text()

    if not content.startswith('---'):
        return False, "SKILL.md missing YAML frontmatter"

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid YAML frontmatter format"

    frontmatter = match.group(1)

    # Check required fields
    if 'name:' not in frontmatter:
        return False, "Missing 'name' in frontmatter"

    if 'description:' not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    # Extract name for validation
    name_match = re.search(r'name:\s*(.+)', frontmatter)
    if name_match:
        name = name_match.group(1).strip()
        # Check naming convention
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"Name '{name}' should be hyphen-case (lowercase, hyphens only)"
        if name.startswith('-') or name.endswith('-') or '--' in name:
            return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"

    return True, "Skill is valid!"


def confirm_finalization(skill_path):
    """
    Ask user to confirm they're ready to finalize the skill.

    Args:
        skill_path: Path to skill directory

    Returns:
        True if user confirms, False otherwise
    """
    skill_name = skill_path.name

    print("\n" + "="*70)
    print("🎯 SKILL FINALIZATION")
    print("="*70)
    print(f"\nSkill: {skill_name}")
    print(f"Path: {skill_path}")
    print("\nFinalization will:")
    print("  1. Validate the skill structure")
    print("  2. Create a timestamped zip file for distribution")
    print("  3. Lock this version with a timestamp")
    print("\nBefore finalizing, ensure you have:")
    print("  ✓ Completed all customizations")
    print("  ✓ Updated CUSTOMIZATION_LOG.md")
    print("  ✓ Tested the skill on real tasks")
    print("  ✓ Documented all changes")
    print("\n" + "-"*70)

    response = input("\nAre you ready to finalize this skill? (yes/no): ").strip().lower()

    return response in ['yes', 'y']


def package_skill_with_timestamp(skill_path, output_dir=None):
    """
    Package a skill into a timestamped zip file.

    Args:
        skill_path: Path to the skill folder
        output_dir: Optional output directory (defaults to current directory)

    Returns:
        Path to the created zip file, or None if error
    """
    skill_path = Path(skill_path).resolve()
    skill_name = skill_path.name

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    # Determine output location
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    zip_filename = output_path / f"{skill_name}-{timestamp}.zip"

    # Create the zip file
    try:
        print(f"\n📦 Packaging skill...")
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the skill directory
            file_count = 0
            for file_path in skill_path.rglob('*'):
                if file_path.is_file():
                    # Calculate the relative path within the zip
                    arcname = file_path.relative_to(skill_path.parent)
                    zipf.write(file_path, arcname)
                    print(f"  ✓ Added: {arcname}")
                    file_count += 1

        print(f"\n✅ Successfully packaged skill!")
        print(f"   Files: {file_count}")
        print(f"   Output: {zip_filename}")
        print(f"   Size: {zip_filename.stat().st_size / 1024:.1f} KB")

        return zip_filename

    except Exception as e:
        print(f"\n❌ Error creating zip file: {e}")
        return None


def print_next_steps(zip_path):
    """Print helpful next steps after finalization."""
    print("\n" + "="*70)
    print("🎉 SKILL FINALIZED!")
    print("="*70)
    print("\n📝 Next steps:")
    print(f"\n1. Install in Claude.ai:")
    print(f"   - Go to claude.ai")
    print(f"   - Click 'Skills' → 'Upload skill'")
    print(f"   - Select: {zip_path.name}")
    print(f"\n2. Install in Claude Desktop:")
    print(f"   - Open Claude Desktop settings")
    print(f"   - Go to 'Skills' section")
    print(f"   - Click 'Install' and select: {zip_path.name}")
    print(f"\n3. Share with others:")
    print(f"   - Send the zip file: {zip_path.name}")
    print(f"   - Recipients can install it the same way")
    print(f"\n4. Version tracking:")
    print(f"   - The timestamp ({zip_path.stem.split('-', 1)[1]}) helps track versions")
    print(f"   - Keep the CUSTOMIZATION_LOG.md updated for future iterations")
    print("\n" + "="*70)


def finalize_skill(skill_path, output_dir=None):
    """
    Complete finalization workflow.

    Args:
        skill_path: Path to skill directory
        output_dir: Optional output directory for zip file

    Returns:
        True if successful, False otherwise
    """
    skill_path = Path(skill_path).resolve()

    # Validate skill directory
    if not skill_path.exists():
        print(f"❌ Error: Skill directory not found: {skill_path}")
        return False

    if not skill_path.is_dir():
        print(f"❌ Error: Path is not a directory: {skill_path}")
        return False

    # Confirm with user
    if not confirm_finalization(skill_path):
        print("\n❌ Finalization cancelled by user.")
        print("   Continue customizing your skill and run this script again when ready.")
        return False

    # Validate skill structure
    print("\n🔍 Validating skill structure...")
    valid, message = validate_skill(skill_path)

    if not valid:
        print(f"❌ Validation failed: {message}")
        print("\n   Please fix the issues and try again.")
        return False

    print(f"✅ {message}")

    # Package the skill
    zip_path = package_skill_with_timestamp(skill_path, output_dir)

    if not zip_path:
        return False

    # Print next steps
    print_next_steps(zip_path)

    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: finalize_skill.py <skill-directory> [--output <output-directory>]")
        print("\nExamples:")
        print("  finalize_skill.py ./my-pdf-workflow")
        print("  finalize_skill.py ./my-pdf-workflow --output ~/Desktop")
        print("  finalize_skill.py ../custom-skills/my-design --output ./dist")
        print("\nThis script:")
        print("  1. Confirms you're ready to finalize")
        print("  2. Validates the skill structure")
        print("  3. Creates a timestamped zip file: {skill-name}-{YYYYMMDD-HHMMSS}.zip")
        sys.exit(1)

    skill_path = sys.argv[1]

    # Parse optional output directory
    output_dir = None
    if '--output' in sys.argv:
        try:
            output_index = sys.argv.index('--output')
            output_dir = sys.argv[output_index + 1]
        except (ValueError, IndexError):
            print("❌ Error: --output flag requires a directory path")
            sys.exit(1)

    print(f"🚀 Finalizing skill: {skill_path}")
    if output_dir:
        print(f"   Output directory: {output_dir}")

    result = finalize_skill(skill_path, output_dir)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
