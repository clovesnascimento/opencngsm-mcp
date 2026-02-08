"""
OpenCngsm v3.1 - Clawdbot Skill Converter
Automatically converts Clawdbot skills to OpenCngsm format
"""
import os
import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import shutil
import logging

# Import config manager for universal paths
try:
    from core.config_manager import config, get_config_dir, get_skills_dir
except ImportError:
    # Fallback if config_manager not available
    def get_config_dir():
        return Path.home() / '.opencngsm'
    
    def get_skills_dir():
        return Path.cwd() / 'skills'

logger = logging.getLogger(__name__)


class ClawdbotSkillConverter:
    """
    Automatic converter for Clawdbot skills to OpenCngsm format
    
    Features:
    - Detects Clawdbot skills (SKILL.md with clawdbot metadata)
    - Converts config paths (~/.clawdbot → universal ~/.opencngsm)
    - Converts bash/curl commands to Python
    - Updates metadata (clawdbot → opencngsm)
    - Generates Python skill wrapper
    """
    
    # Universal path mappings (cross-platform)
    @staticmethod
    def get_path_mappings() -> Dict[str, str]:
        """Get platform-independent path mappings"""
        config_dir = get_config_dir()
        
        return {
            '~/.clawdbot/clawdbot.json': str(config_dir / 'config.json'),
            '~/.clawdbot/': str(config_dir) + '/',
            'clawdbot.json': 'config.json',
            'clawdbot gateway': 'opencngsm gateway',
            'Clawdbot': 'OpenCngsm',
            'clawdbot': 'opencngsm',
            'CLAWDBOT': 'OPENCNGSM',
        }

    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize converter
        
        Args:
            output_dir: Directory to save converted skills (default: auto-detected skills dir)
        """
        if output_dir is None:
            # Use universal skills directory
            self.output_dir = get_skills_dir()
        else:
            self.output_dir = Path(output_dir)
        
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Get dynamic path mappings
        self.PATH_MAPPINGS = self.get_path_mappings()
    
    def is_clawdbot_skill(self, skill_path: Path) -> bool:
        """
        Check if skill is a Clawdbot skill
        
        Args:
            skill_path: Path to skill directory
        
        Returns:
            True if Clawdbot skill
        """
        skill_md = skill_path / 'SKILL.md'
        
        if not skill_md.exists():
            return False
        
        content = skill_md.read_text(encoding='utf-8')
        
        # Check for clawdbot metadata
        if 'clawdbot' in content.lower():
            return True
        
        # Check YAML frontmatter
        if content.startswith('---'):
            try:
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    if isinstance(frontmatter, dict):
                        metadata = frontmatter.get('metadata', {})
                        if 'clawdbot' in metadata:
                            return True
            except:
                pass
        
        return False
    
    def convert_skill(self, skill_path: Path, auto_python: bool = True) -> Path:
        """
        Convert Clawdbot skill to OpenCngsm format
        
        Args:
            skill_path: Path to Clawdbot skill directory
            auto_python: If True, generate Python wrapper for bash/curl commands
        
        Returns:
            Path to converted skill
        
        Example:
            converter = ClawdbotSkillConverter()
            output_path = converter.convert_skill(Path('AG/hack'))
        """
        if not self.is_clawdbot_skill(skill_path):
            raise ValueError(f"Not a Clawdbot skill: {skill_path}")
        
        skill_name = skill_path.name
        logger.info(f"🔄 Converting Clawdbot skill: {skill_name}")
        
        # Create output directory
        output_path = self.output_dir / skill_name
        output_path.mkdir(exist_ok=True)
        
        # Convert SKILL.md
        self._convert_skill_md(skill_path, output_path)
        
        # Copy other files
        self._copy_additional_files(skill_path, output_path)
        
        # Generate Python wrapper if needed
        if auto_python:
            self._generate_python_wrapper(skill_path, output_path)
        
        logger.info(f"✅ Converted skill saved to: {output_path}")
        return output_path
    
    def _convert_skill_md(self, skill_path: Path, output_path: Path):
        """Convert SKILL.md file"""
        skill_md = skill_path / 'SKILL.md'
        content = skill_md.read_text(encoding='utf-8')
        
        # Parse frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter_text = parts[1]
                body = parts[2]
                
                # Convert frontmatter
                frontmatter = yaml.safe_load(frontmatter_text)
                frontmatter = self._convert_frontmatter(frontmatter)
                
                # Convert body
                body = self._convert_text(body)
                
                # Reconstruct
                new_frontmatter = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
                content = f"---\n{new_frontmatter}---{body}"
        else:
            # No frontmatter, just convert text
            content = self._convert_text(content)
        
        # Save
        output_md = output_path / 'SKILL.md'
        output_md.write_text(content, encoding='utf-8')
        logger.info(f"📝 Converted SKILL.md")
    
    def _convert_frontmatter(self, frontmatter: Dict) -> Dict:
        """Convert frontmatter metadata"""
        # Convert metadata.clawdbot → metadata.opencngsm
        if 'metadata' in frontmatter:
            metadata = frontmatter['metadata']
            
            if 'clawdbot' in metadata:
                metadata['opencngsm'] = metadata.pop('clawdbot')
        
        return frontmatter
    
    def _convert_text(self, text: str) -> str:
        """Convert text content (paths, references)"""
        for old, new in self.PATH_MAPPINGS.items():
            text = text.replace(old, new)
        
        return text
    
    def _copy_additional_files(self, skill_path: Path, output_path: Path):
        """Copy additional files (excluding SKILL.md)"""
        for item in skill_path.iterdir():
            if item.name == 'SKILL.md':
                continue
            
            if item.is_file():
                shutil.copy2(item, output_path / item.name)
                logger.info(f"📄 Copied: {item.name}")
            elif item.is_dir():
                shutil.copytree(item, output_path / item.name, dirs_exist_ok=True)
                logger.info(f"📁 Copied directory: {item.name}")
    
    def _generate_python_wrapper(self, skill_path: Path, output_path: Path):
        """Generate Python wrapper for bash/curl commands"""
        skill_md = skill_path / 'SKILL.md'
        content = skill_md.read_text(encoding='utf-8')
        
        # Detect if skill uses curl/bash
        has_curl = 'curl' in content.lower()
        has_bash = '```bash' in content or '#!/bin/bash' in content
        
        if not (has_curl or has_bash):
            logger.info("⏭️ No bash/curl detected, skipping Python wrapper")
            return
        
        # Extract skill name
        skill_name = output_path.name
        
        # Generate Python wrapper
        wrapper_code = self._generate_wrapper_code(skill_name, content)
        
        # Save
        wrapper_file = output_path / f'{skill_name}_skill.py'
        wrapper_file.write_text(wrapper_code, encoding='utf-8')
        logger.info(f"🐍 Generated Python wrapper: {wrapper_file.name}")
    
    def _generate_wrapper_code(self, skill_name: str, skill_md_content: str) -> str:
        """Generate Python wrapper code"""
        class_name = ''.join(word.capitalize() for word in skill_name.replace('-', '_').split('_')) + 'Skill'
        
        # Extract curl commands
        curl_commands = self._extract_curl_commands(skill_md_content)
        
        # Generate methods
        methods = []
        for i, cmd in enumerate(curl_commands):
            method = self._curl_to_python_method(cmd, i)
            if method:
                methods.append(method)
        
        # Template
        template = f'''"""
OpenCngsm v3.1 - {skill_name.replace('-', ' ').title()} Skill
Auto-generated from Clawdbot skill
"""
import os
import json
import subprocess
import requests
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

# Import config manager for universal paths
try:
    from core.config_manager import config
except ImportError:
    # Fallback
    class FallbackConfig:
        @staticmethod
        def get_path(key):
            return Path.home() / '.opencngsm' / 'config.json'
    config = FallbackConfig()

logger = logging.getLogger(__name__)


class {class_name}:
    """
    {skill_name.replace('-', ' ').title()} skill
    
    Auto-converted from Clawdbot skill format
    """
    
    def __init__(self):
        """Initialize skill"""
        # Use universal config path
        try:
            self.config_path = config.config_file
        except:
            self.config_path = Path.home() / '.opencngsm' / 'config.json'
    
    def read_config(self) -> Dict:
        """Read OpenCngsm config"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {{self.config_path}}")
        
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def write_config(self, config_data: Dict):
        """Write OpenCngsm config"""
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def run_shell(self, command: str) -> str:
        """Run shell command"""
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Command failed: {{result.stderr}}")
        
        return result.stdout
    
{chr(10).join(methods)}


# Example usage
if __name__ == "__main__":
    skill = {class_name}()
    # Add usage examples here
'''
        
        return template
    
    def _extract_curl_commands(self, content: str) -> List[str]:
        """Extract curl commands from markdown"""
        commands = []
        
        # Find bash code blocks
        bash_blocks = re.findall(r'```bash\n(.*?)\n```', content, re.DOTALL)
        
        for block in bash_blocks:
            # Find curl commands
            curl_cmds = re.findall(r'curl[^\n]+(?:\\\n[^\n]+)*', block)
            commands.extend(curl_cmds)
        
        return commands
    
    def _curl_to_python_method(self, curl_cmd: str, index: int) -> Optional[str]:
        """Convert curl command to Python method"""
        # Simple conversion (can be enhanced)
        
        # Extract URL
        url_match = re.search(r'"(https?://[^"]+)"', curl_cmd)
        if not url_match:
            return None
        
        url = url_match.group(1)
        
        # Detect method
        if '-X POST' in curl_cmd or '--request POST' in curl_cmd:
            method = 'POST'
        elif '-X GET' in curl_cmd:
            method = 'GET'
        else:
            method = 'GET'
        
        # Generate method name
        method_name = f'api_call_{index + 1}'
        
        template = f'''    async def {method_name}(self, **kwargs) -> Dict:
        """
        API call (auto-generated)
        
        Original curl command:
        {curl_cmd[:100]}...
        """
        url = "{url}"
        
        # Replace placeholders
        for key, value in kwargs.items():
            url = url.replace(f'{{{{key}}}}', str(value))
        
        response = requests.{method.lower()}(url)
        response.raise_for_status()
        
        return response.json()
'''
        
        return template
    
    def batch_convert(self, skills_dir: Path) -> List[Path]:
        """
        Convert all Clawdbot skills in directory
        
        Args:
            skills_dir: Directory containing Clawdbot skills
        
        Returns:
            List of converted skill paths
        """
        converted = []
        
        for item in skills_dir.iterdir():
            if item.is_dir() and self.is_clawdbot_skill(item):
                try:
                    output_path = self.convert_skill(item)
                    converted.append(output_path)
                except Exception as e:
                    logger.error(f"❌ Failed to convert {item.name}: {e}")
        
        logger.info(f"✅ Converted {len(converted)} skills")
        return converted


# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python clawdbot_converter.py <skill_path>")
        sys.exit(1)
    
    skill_path = Path(sys.argv[1])
    
    converter = ClawdbotSkillConverter()
    
    if skill_path.is_dir():
        # Single skill
        output = converter.convert_skill(skill_path)
        print(f"✅ Converted to: {output}")
    else:
        print(f"❌ Not a directory: {skill_path}")
        sys.exit(1)
