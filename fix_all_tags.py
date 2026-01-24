#!/usr/bin/env python3
"""
Obsidian 태그 일괄 수정 스크립트
- 02-study: 이모지 메타데이터를 YAML frontmatter로 변환
- 04-interview: 쉼표로 구분된 태그를 YAML 배열 형식으로 변환

사용법:
    cd /Volumes/DEV_DATA/code-notes
    python3 fix_all_tags.py
"""

import re
from pathlib import Path

# =============================================================================
# 02-STUDY 파일 처리
# =============================================================================

def extract_study_metadata(content):
    """Study 파일에서 메타데이터 추출"""
    metadata = {
        'tags': ['study'],
        'created': '2026-01-23',
        'difficulty': '중'
    }
    
    # 기술 카테고리
    match = re.search(r'🏷️기술 카테고리:\s*([^\n]+)', content)
    if match:
        cats = [cat.strip() for cat in match.group(1).split(',')]
        for cat in cats:
            tag = cat.lower().strip().replace(' ', '-')
            if tag and tag not in metadata['tags']:
                metadata['tags'].append(tag)
    
    # 핵심키워드
    match = re.search(r'💡핵심키워드:\s*([^\n]+)', content)
    if match:
        keywords = re.findall(r'#(\w+)', match.group(1))
        for kw in keywords:
            tag = kw.lower().replace('_', '-')
            if tag not in metadata['tags']:
                metadata['tags'].append(tag)
    
    # 난이도
    match = re.search(r'💼 면접 빈출도:\s*(\S+)', content)
    if match:
        level = match.group(1)
        if '최상' in level:
            metadata['difficulty'] = '상'
        elif '상' in level:
            metadata['difficulty'] = '상'
        elif '중' in level:
            metadata['difficulty'] = '중'
        elif '하' in level:
            metadata['difficulty'] = '하'
    
    # 날짜
    match = re.search(r'날짜:\s*(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', content)
    if match:
        y, m, d = match.groups()
        metadata['created'] = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
    else:
        # 작성일 패턴
        match = re.search(r'\*\*작성일\*\*:\s*(\d{4})-(\d{1,2})-(\d{1,2})', content)
        if match:
            y, m, d = match.groups()
            metadata['created'] = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
    
    return metadata

def convert_study_file(filepath):
    """Study 파일을 YAML frontmatter 형식으로 변환"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 이미 YAML frontmatter가 있으면 스킵
        if content.startswith('---\n'):
            return False, "이미 YAML 형식"
        
        # 메타데이터 추출
        metadata = extract_study_metadata(content)
        
        # 첫 번째 제목(#)부터 본문 시작
        lines = content.split('\n')
        main_start = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('# ') and not line.strip().startswith('## '):
                main_start = i
                break
        
        if main_start == -1:
            return False, "제목을 찾을 수 없음"
        
        main_content = '\n'.join(lines[main_start:])
        
        # YAML frontmatter 생성
        yaml_lines = ['---', 'tags:']
        for tag in metadata['tags']:
            yaml_lines.append(f'  - {tag}')
        yaml_lines.append(f"created: {metadata['created']}")
        yaml_lines.append(f"difficulty: {metadata['difficulty']}")
        yaml_lines.append('---')
        yaml_lines.append('')
        
        new_content = '\n'.join(yaml_lines) + main_content
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, "변환 완료"
        
    except Exception as e:
        return False, f"오류: {str(e)}"

# =============================================================================
# 04-INTERVIEW 파일 처리
# =============================================================================

def fix_interview_tags(filepath):
    """Interview 파일의 쉼표 구분 태그를 YAML 배열로 변환"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # YAML frontmatter가 없으면 추가
        if not content.startswith('---\n'):
            yaml_front = """---
tags:
  - interview
created: 2026-01-23
difficulty: 중
---

"""
            new_content = yaml_front + content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True, "YAML 추가"
        
        # tags 라인 찾기
        lines = content.split('\n')
        if len(lines) < 3:
            return False, "파일이 너무 짧음"
        
        # tags: xxx, yyy 형식 찾기
        for i, line in enumerate(lines[:10]):  # frontmatter는 보통 처음 10줄 안에
            if line.startswith('tags:') and ',' in line:
                # 쉼표로 구분된 태그 발견
                tags_str = line.split('tags:')[1].strip()
                tags = [t.strip() for t in tags_str.split(',')]
                
                # YAML 배열 형식으로 변경
                new_lines = lines[:i]  # tags 라인 이전까지
                new_lines.append('tags:')
                for tag in tags:
                    new_lines.append(f'  - {tag}')
                new_lines.extend(lines[i+1:])  # tags 라인 이후
                
                new_content = '\n'.join(new_lines)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                return True, "태그 형식 수정"
        
        return False, "수정 불필요"
        
    except Exception as e:
        return False, f"오류: {str(e)}"

# =============================================================================
# 메인 실행
# =============================================================================

def main():
    root = Path('/Volumes/DEV_DATA/code-notes')
    
    print("=" * 70)
    print("Obsidian 태그 일괄 수정 스크립트")
    print("=" * 70)
    print()
    
    # 02-study 처리
    print("📚 02-study 파일 변환 중...")
    print("-" * 70)
    
    study_dir = root / '02-study'
    if not study_dir.exists():
        print(f"❌ {study_dir} 디렉토리를 찾을 수 없습니다.")
        return
    
    study_success = 0
    study_skip = 0
    study_error = 0
    
    for filepath in sorted(study_dir.rglob('*.md')):
        rel_path = filepath.relative_to(root)
        success, msg = convert_study_file(filepath)
        
        if success:
            print(f"✅ {rel_path}")
            study_success += 1
        elif "이미 YAML" in msg:
            study_skip += 1
        else:
            print(f"❌ {rel_path}: {msg}")
            study_error += 1
    
    print()
    print(f"📊 02-study 결과:")
    print(f"   ✅ 변환 완료: {study_success}개")
    print(f"   ⏭️  이미 변환됨: {study_skip}개")
    print(f"   ❌ 오류: {study_error}개")
    print()
    
    # 04-interview 처리
    print("📝 04-interview 파일 수정 중...")
    print("-" * 70)
    
    interview_dir = root / '04-interview'
    if not interview_dir.exists():
        print(f"❌ {interview_dir} 디렉토리를 찾을 수 없습니다.")
        return
    
    interview_fixed = 0
    interview_skip = 0
    interview_error = 0
    
    for filepath in sorted(interview_dir.rglob('*.md')):
        rel_path = filepath.relative_to(root)
        success, msg = fix_interview_tags(filepath)
        
        if success:
            print(f"🔧 {rel_path}: {msg}")
            interview_fixed += 1
        elif "수정 불필요" in msg:
            interview_skip += 1
        else:
            print(f"❌ {rel_path}: {msg}")
            interview_error += 1
    
    print()
    print(f"📊 04-interview 결과:")
    print(f"   🔧 수정 완료: {interview_fixed}개")
    print(f"   ⏭️  수정 불필요: {interview_skip}개")
    print(f"   ❌ 오류: {interview_error}개")
    print()
    
    # 전체 요약
    print("=" * 70)
    print("✨ 전체 작업 완료!")
    print("=" * 70)
    total_success = study_success + interview_fixed
    total_files = study_success + study_skip + study_error + interview_fixed + interview_skip + interview_error
    print(f"📁 총 {total_files}개 파일 중 {total_success}개 수정됨")
    print()
    print("💡 Obsidian을 재시작하여 태그 인덱스를 갱신하세요!")
    print()

if __name__ == '__main__':
    main()
