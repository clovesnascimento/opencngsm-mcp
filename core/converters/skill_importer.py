"""
OpenCngsm v3.1 - Skill Import CLI
Command-line interface for importing and converting skills
"""
import click
import sys
from pathlib import Path
from core.converters.clawdbot_converter import ClawdbotSkillConverter
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """OpenCngsm Skill Import Tool"""
    pass


@cli.command()
@click.argument('skill_path', type=click.Path(exists=True))
@click.option('--output', '-o', default='skills', help='Output directory')
@click.option('--no-python', is_flag=True, help='Skip Python wrapper generation')
def import_skill(skill_path, output, no_python):
    """
    Import a Clawdbot skill and convert to OpenCngsm format
    
    Example:
        opencngsm import-skill C:/Users/cngsm/Desktop/XXX/AG/hack
    """
    skill_path = Path(skill_path)
    
    if not skill_path.is_dir():
        click.echo(f"❌ Not a directory: {skill_path}", err=True)
        sys.exit(1)
    
    converter = ClawdbotSkillConverter(output_dir=output)
    
    # Check if Clawdbot skill
    if not converter.is_clawdbot_skill(skill_path):
        click.echo(f"⚠️ Not a Clawdbot skill: {skill_path}")
        click.echo("Attempting to import as generic skill...")
    
    try:
        output_path = converter.convert_skill(skill_path, auto_python=not no_python)
        click.echo(f"✅ Skill imported successfully!")
        click.echo(f"📁 Location: {output_path}")
        click.echo(f"\n🎯 Next steps:")
        click.echo(f"1. Review converted skill: {output_path / 'SKILL.md'}")
        click.echo(f"2. Test the skill")
        click.echo(f"3. Add to OpenCngsm registry")
    except Exception as e:
        click.echo(f"❌ Import failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('skills_dir', type=click.Path(exists=True))
@click.option('--output', '-o', default='skills', help='Output directory')
def import_batch(skills_dir, output):
    """
    Import all Clawdbot skills from a directory
    
    Example:
        opencngsm import-batch C:/Users/cngsm/Desktop/XXX/AG
    """
    skills_dir = Path(skills_dir)
    
    if not skills_dir.is_dir():
        click.echo(f"❌ Not a directory: {skills_dir}", err=True)
        sys.exit(1)
    
    converter = ClawdbotSkillConverter(output_dir=output)
    
    try:
        converted = converter.batch_convert(skills_dir)
        
        click.echo(f"\n✅ Batch import complete!")
        click.echo(f"📊 Converted {len(converted)} skills:")
        
        for path in converted:
            click.echo(f"  - {path.name}")
        
        if converted:
            click.echo(f"\n🎯 Next steps:")
            click.echo(f"1. Review converted skills in: {output}")
            click.echo(f"2. Test each skill")
            click.echo(f"3. Add to OpenCngsm registry")
    except Exception as e:
        click.echo(f"❌ Batch import failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('skill_path', type=click.Path(exists=True))
def check(skill_path):
    """
    Check if a skill is a Clawdbot skill
    
    Example:
        opencngsm check C:/Users/cngsm/Desktop/XXX/AG/hack
    """
    skill_path = Path(skill_path)
    
    converter = ClawdbotSkillConverter()
    
    if converter.is_clawdbot_skill(skill_path):
        click.echo(f"✅ Clawdbot skill detected: {skill_path.name}")
        
        # Show metadata
        skill_md = skill_path / 'SKILL.md'
        content = skill_md.read_text(encoding='utf-8')
        
        if content.startswith('---'):
            import yaml
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                
                click.echo(f"\n📋 Metadata:")
                click.echo(f"  Name: {frontmatter.get('name', 'N/A')}")
                click.echo(f"  Description: {frontmatter.get('description', 'N/A')[:60]}...")
                
                metadata = frontmatter.get('metadata', {})
                if 'clawdbot' in metadata:
                    clawdbot = metadata['clawdbot']
                    click.echo(f"  Emoji: {clawdbot.get('emoji', 'N/A')}")
                    
                    requires = clawdbot.get('requires', {})
                    if requires:
                        click.echo(f"  Dependencies:")
                        if 'bins' in requires:
                            click.echo(f"    Binaries: {', '.join(requires['bins'])}")
                        if 'env' in requires:
                            click.echo(f"    Env vars: {', '.join(requires['env'])}")
    else:
        click.echo(f"❌ Not a Clawdbot skill: {skill_path.name}")
        sys.exit(1)


if __name__ == '__main__':
    cli()
