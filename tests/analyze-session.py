#!/usr/bin/env python3
"""
Analyze Claude Code session transcripts.
Parses .jsonl files to extract useful information.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime


def load_session(session_file):
    """Load session from JSONL file."""
    messages = []
    with open(session_file, 'r') as f:
        for line in f:
            if line.strip():
                messages.append(json.loads(line))
    return messages


def extract_tool_invocations(messages):
    """Extract all tool invocations from session."""
    tools = []
    for msg in messages:
        if msg.get('type') == 'assistant':
            content = msg.get('message', {}).get('content', [])
            if isinstance(content, list):
                for item in content:
                    if item.get('type') == 'tool_use':
                        tools.append({
                            'name': item.get('name'),
                            'input': item.get('input', {}),
                            'id': item.get('id')
                        })
    return tools


def extract_skill_invocations(messages):
    """Extract Skill tool invocations."""
    skills = []
    for msg in messages:
        if msg.get('type') == 'assistant':
            content = msg.get('message', {}).get('content', [])
            if isinstance(content, list):
                for item in content:
                    if item.get('type') == 'tool_use' and item.get('name') == 'Skill':
                        input_data = item.get('input', {})
                        skills.append({
                            'skill': input_data.get('skill'),
                            'args': input_data.get('args', ''),
                            'id': item.get('id')
                        })
    return skills


def calculate_token_usage(messages):
    """Calculate total token usage from session."""
    total_input = 0
    total_output = 0
    cache_read = 0
    cache_creation = 0

    for msg in messages:
        usage = msg.get('message', {}).get('usage', {})
        if usage:
            total_input += usage.get('input_tokens', 0)
            total_output += usage.get('output_tokens', 0)
            cache_read += usage.get('cache_read_input_tokens', 0)
            cache_creation += usage.get('cache_creation_input_tokens', 0)

    return {
        'input': total_input,
        'output': total_output,
        'cache_read': cache_read,
        'cache_creation': cache_creation,
        'total': total_input + total_output
    }


def extract_user_messages(messages):
    """Extract all user messages."""
    user_msgs = []
    for msg in messages:
        if msg.get('type') == 'user':
            content = msg.get('message', {}).get('content', [])
            if isinstance(content, list):
                for item in content:
                    if item.get('type') == 'text':
                        user_msgs.append(item.get('text', ''))
    return user_msgs


def extract_assistant_messages(messages):
    """Extract all assistant messages."""
    assistant_msgs = []
    for msg in messages:
        if msg.get('type') == 'assistant':
            content = msg.get('message', {}).get('content', [])
            if isinstance(content, list):
                text_parts = []
                for item in content:
                    if item.get('type') == 'text':
                        text_parts.append(item.get('text', ''))
                if text_parts:
                    assistant_msgs.append('\n'.join(text_parts))
    return assistant_msgs


def analyze_session(session_file, verbose=False):
    """Analyze a session file and print results."""
    if not os.path.exists(session_file):
        print(f"Error: Session file not found: {session_file}")
        return None

    messages = load_session(session_file)

    print(f"\nSession: {os.path.basename(session_file)}")
    print(f"Total messages: {len(messages)}")

    # Token usage
    usage = calculate_token_usage(messages)
    print(f"\n--- Token Usage ---")
    print(f"  Input:        {usage['input']:,}")
    print(f"  Output:       {usage['output']:,}")
    print(f"  Cache read:   {usage['cache_read']:,}")
    print(f"  Cache create: {usage['cache_creation']:,}")
    print(f"  Total:        {usage['total']:,}")

    # Skills invoked
    skills = extract_skill_invocations(messages)
    print(f"\n--- Skills Invoked ({len(skills)}) ---")
    if skills:
        for skill in skills:
            args_preview = skill['args'][:50] + '...' if len(skill.get('args', '')) > 50 else skill.get('args', '')
            print(f"  - {skill['skill']}: {args_preview}")
    else:
        print("  (none)")

    # Tools invoked
    tools = extract_tool_invocations(messages)
    tool_counts = {}
    for tool in tools:
        name = tool['name']
        tool_counts[name] = tool_counts.get(name, 0) + 1

    print(f"\n--- Tools Invoked ---")
    for tool_name, count in sorted(tool_counts.items(), key=lambda x: -x[1]):
        print(f"  {tool_name}: {count}")

    if verbose:
        print(f"\n--- User Messages ---")
        for i, msg in enumerate(extract_user_messages(messages)[:5]):
            print(f"  {i+1}. {msg[:100]}...")

        print(f"\n--- Assistant Messages ---")
        for i, msg in enumerate(extract_assistant_messages(messages)[:3]):
            print(f"  {i+1}. {msg[:100]}...")

    return {
        'message_count': len(messages),
        'usage': usage,
        'skills': skills,
        'tools': tool_counts
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Analyze Claude Code session transcripts')
    parser.add_argument('session_file', help='Path to session .jsonl file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose output')
    parser.add_argument('--check-skill', help='Check if specific skill was invoked')

    args = parser.parse_args()

    result = analyze_session(args.session_file, args.verbose)

    if args.check_skill and result:
        skill_found = any(s['skill'] == args.check_skill for s in result.get('skills', []))
        if skill_found:
            print(f"\n✓ Skill '{args.check_skill}' was invoked")
            sys.exit(0)
        else:
            print(f"\n✗ Skill '{args.check_skill}' was NOT invoked")
            sys.exit(1)


if __name__ == '__main__':
    main()
