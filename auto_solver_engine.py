#!/usr/bin/env python3
"""
🤖 AUTO-SOLVER ENGINE
====================
محرك حل تلقائي للمشاكل البسيطة

القدرات:
- Documentation fixes (typos, grammar, formatting)
- Configuration files (JSON, YAML, TOML)
- Simple bug fixes (obvious errors)
- Test improvements
- CI/CD fixes
"""

import os
import re
import json
import yaml
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import anthropic
from github import Github

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Solution:
    """Représente une solution à un problème"""
    issue_url: str
    solution_type: str  # doc, config, bug, test
    files_to_change: List[Dict]  # [{path, old_content, new_content, explanation}]
    pr_title: str
    pr_description: str
    confidence: float
    estimated_time: int  # minutes

# ============================================================================
# AUTO-SOLVER ENGINE
# ============================================================================

class AutoSolverEngine:
    """Moteur de résolution automatique"""
    
    def __init__(self, github_token: str, anthropic_key: str):
        self.github = Github(github_token)
        self.client = anthropic.Anthropic(api_key=anthropic_key)
        self.logger = logging.getLogger("AutoSolver")
        
        # Solvable patterns
        self.solvable_patterns = {
            'typo': {
                'keywords': ['typo', 'spelling', 'grammar', 'misspell'],
                'files': ['.md', '.txt', '.rst'],
                'confidence': 0.9
            },
            'json_format': {
                'keywords': ['json', 'invalid json', 'parse error'],
                'files': ['.json'],
                'confidence': 0.85
            },
            'yaml_format': {
                'keywords': ['yaml', 'yml', 'invalid yaml'],
                'files': ['.yaml', '.yml'],
                'confidence': 0.85
            },
            'broken_link': {
                'keywords': ['broken link', '404', 'dead link'],
                'files': ['.md', '.html'],
                'confidence': 0.8
            },
            'missing_import': {
                'keywords': ['import error', 'module not found', 'cannot import'],
                'files': ['.py', '.js', '.ts'],
                'confidence': 0.7
            }
        }
    
    def can_solve(self, issue_title: str, issue_body: str, labels: List[str]) -> Tuple[bool, str, float]:
        """Détermine si on peut résoudre automatiquement"""
        text = f"{issue_title} {issue_body}".lower()
        label_text = ' '.join(labels).lower()
        
        for pattern_name, pattern_info in self.solvable_patterns.items():
            # Check keywords
            if any(kw in text or kw in label_text for kw in pattern_info['keywords']):
                return True, pattern_name, pattern_info['confidence']
        
        return False, "unknown", 0.0
    
    async def generate_solution(self, repo_name: str, issue_number: int) -> Optional[Solution]:
        """Génère une solution automatique"""
        try:
            repo = self.github.get_repo(repo_name)
            issue = repo.get_issue(issue_number)
            
            # Check if solvable
            can_solve, solution_type, confidence = self.can_solve(
                issue.title, 
                issue.body or "", 
                [l.name for l in issue.labels]
            )
            
            if not can_solve or confidence < 0.7:
                self.logger.info(f"Cannot auto-solve: {issue.title}")
                return None
            
            self.logger.info(f"🤖 Attempting auto-solve: {solution_type} (confidence: {confidence:.2%})")
            
            # Use Claude to generate solution
            solution_prompt = f"""You are an expert programmer. A GitHub issue needs to be solved.

**Issue Title:** {issue.title}
**Issue Body:**
{issue.body or 'No description'}

**Issue Type:** {solution_type}
**Repository:** {repo_name}

**Your Task:**
1. Analyze the issue
2. Determine which files need to be changed
3. Generate the exact changes needed
4. Create a PR title and description

**Response Format (JSON):**
{{
    "solvable": true/false,
    "reasoning": "why this can/cannot be solved",
    "files_to_change": [
        {{
            "path": "path/to/file",
            "changes": "description of changes",
            "search_pattern": "text to find",
            "replacement": "text to replace with"
        }}
    ],
    "pr_title": "fix: Title of PR",
    "pr_description": "Detailed description of changes",
    "estimated_time": 15
}}

Be specific and accurate. Only return valid JSON."""

            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.2,
                messages=[{"role": "user", "content": solution_prompt}]
            )
            
            response_text = message.content[0].text
            
            # Extract JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                self.logger.error("No JSON found in Claude response")
                return None
            
            solution_data = json.loads(json_match.group())
            
            if not solution_data.get('solvable', False):
                self.logger.info(f"Claude says not solvable: {solution_data.get('reasoning')}")
                return None
            
            # Create solution object
            solution = Solution(
                issue_url=issue.html_url,
                solution_type=solution_type,
                files_to_change=solution_data.get('files_to_change', []),
                pr_title=solution_data.get('pr_title', f"fix: Resolve #{issue_number}"),
                pr_description=solution_data.get('pr_description', ''),
                confidence=confidence,
                estimated_time=solution_data.get('estimated_time', 30)
            )
            
            return solution
            
        except Exception as e:
            self.logger.error(f"Error generating solution: {e}")
            return None
    
    def apply_solution(self, solution: Solution, repo_name: str, issue_number: int) -> bool:
        """Applique la solution et créé une PR"""
        try:
            repo = self.github.get_repo(repo_name)
            
            # Get default branch
            default_branch = repo.default_branch
            base_sha = repo.get_branch(default_branch).commit.sha
            
            # Create new branch
            branch_name = f"fix/issue-{issue_number}-auto"
            try:
                ref = repo.create_git_ref(f"refs/heads/{branch_name}", base_sha)
            except Exception as e:
                if "Reference already exists" in str(e):
                    self.logger.warning(f"Branch {branch_name} already exists")
                    return False
                raise
            
            # Apply changes to files
            for file_change in solution.files_to_change:
                file_path = file_change['path']
                
                try:
                    # Get current file content
                    file = repo.get_contents(file_path, ref=default_branch)
                    current_content = file.decoded_content.decode('utf-8')
                    
                    # Apply changes
                    search = file_change.get('search_pattern', '')
                    replace = file_change.get('replacement', '')
                    
                    if search and replace:
                        new_content = current_content.replace(search, replace)
                    else:
                        # If no pattern, use the whole content as new
                        new_content = file_change.get('new_content', current_content)
                    
                    # Update file in new branch
                    repo.update_file(
                        path=file_path,
                        message=f"fix: {file_change.get('changes', 'Update file')}",
                        content=new_content,
                        sha=file.sha,
                        branch=branch_name
                    )
                    
                    self.logger.info(f"✅ Updated {file_path}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to update {file_path}: {e}")
                    continue
            
            # Create Pull Request
            pr_body = f"""{solution.pr_description}

---
**Automated Solution**
- Issue: #{issue_number}
- Type: {solution.solution_type}
- Confidence: {solution.confidence:.0%}
- Estimated time: {solution.estimated_time} minutes

🤖 This PR was automatically generated by the Auto-Solver Engine.
"""
            
            pr = repo.create_pull(
                title=solution.pr_title,
                body=pr_body,
                head=branch_name,
                base=default_branch
            )
            
            self.logger.info(f"🎉 Created PR: {pr.html_url}")
            
            # Comment on the issue
            issue = repo.get_issue(issue_number)
            issue.create_comment(
                f"👋 Hi! I've analyzed this issue and created an automated fix.\n\n"
                f"**Pull Request:** {pr.html_url}\n\n"
                f"The solution includes:\n"
                f"{''.join('- ' + f['changes'] + '\\n' for f in solution.files_to_change)}\n"
                f"Please review and let me know if any adjustments are needed!"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply solution: {e}")
            return False

# ============================================================================
# SIMPLE SOLVERS
# ============================================================================

class TypoSolver:
    """Solveur spécialisé pour les typos"""
    
    @staticmethod
    def find_typos(text: str) -> List[Dict]:
        """Trouve les typos communes"""
        common_typos = {
            'recieve': 'receive',
            'occured': 'occurred',
            'seperate': 'separate',
            'definately': 'definitely',
            'untill': 'until',
            'occurence': 'occurrence',
            'refrence': 'reference',
            'sucessful': 'successful',
            'acheive': 'achieve',
            'arguement': 'argument',
        }
        
        found = []
        for wrong, correct in common_typos.items():
            if wrong in text.lower():
                found.append({
                    'wrong': wrong,
                    'correct': correct,
                    'context': text[max(0, text.lower().find(wrong)-20):text.lower().find(wrong)+len(wrong)+20]
                })
        
        return found

class JSONSolver:
    """Solveur pour les problèmes JSON"""
    
    @staticmethod
    def fix_json(content: str) -> Tuple[bool, str, str]:
        """Tente de réparer un JSON invalide"""
        try:
            # Try to parse
            json.loads(content)
            return True, content, "JSON is already valid"
        except json.JSONDecodeError as e:
            error_msg = str(e)
            
            # Common fixes
            fixes = []
            
            # Trailing commas
            if "trailing comma" in error_msg.lower():
                fixed = re.sub(r',(\s*[}\]])', r'\1', content)
                fixes.append("Removed trailing commas")
                content = fixed
            
            # Missing commas
            if "expecting ',' delimiter" in error_msg.lower():
                # This is harder to fix automatically
                return False, content, "Missing commas - manual fix needed"
            
            # Try to parse again
            try:
                json.loads(content)
                return True, content, "; ".join(fixes)
            except json.JSONDecodeError:
                return False, content, "Could not auto-fix JSON"

class YAMLSolver:
    """Solveur pour les problèmes YAML"""
    
    @staticmethod
    def fix_yaml(content: str) -> Tuple[bool, str, str]:
        """Tente de réparer un YAML invalide"""
        try:
            yaml.safe_load(content)
            return True, content, "YAML is already valid"
        except yaml.YAMLError as e:
            error_msg = str(e)
            
            # Common fixes
            if "tab character" in error_msg.lower():
                fixed = content.replace('\t', '  ')  # Replace tabs with spaces
                try:
                    yaml.safe_load(fixed)
                    return True, fixed, "Replaced tabs with spaces"
                except yaml.YAMLError:
                    return False, content, "Could not auto-fix YAML"
            
            return False, content, f"YAML error: {error_msg}"

# ============================================================================
# TESTING
# ============================================================================

async def test_auto_solver():
    """Test the auto-solver"""
    github_token = os.getenv("GITHUB_TOKEN", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    
    if not github_token or not anthropic_key:
        print("❌ Missing API keys")
        return
    
    solver = AutoSolverEngine(github_token, anthropic_key)
    
    # Test with a sample repo/issue
    # solution = await solver.generate_solution("test-repo", 123)
    # if solution:
    #     print(f"✅ Generated solution: {solution.pr_title}")
    #     success = solver.apply_solution(solution, "test-repo", 123)
    #     print(f"Applied: {success}")
    
    print("✅ Auto-solver initialized")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_auto_solver())
