#!/usr/bin/env python3
"""Print a copyable GitHub Pages URL and configuration link in Actions Summary."""
import os
from pathlib import Path


def main():
    full = os.environ['GITHUB_REPOSITORY']
    owner, repo = full.split('/', 1)
    url = (f'https://{owner.lower()}.github.io/{repo}/'
           if repo.lower() != f'{owner.lower()}.github.io'
           else f'https://{owner.lower()}.github.io/')
    settings = f'https://github.com/{full}/settings/pages'
    summary = (f'## OpenRank ポータルのPages URL 🌐\n\n'
               f'このURLをコピーして公開サイトを確認してください。\n\n'
               f'```text\n{url}\n```\n\n'
               f'[サイトを開く]({url}) · [Pagesの設定を開く]({settings})\n\n'
               f'> **404の場合**: Settings → Pages → Deploy from a branch → main → /(root) → Save。'
               f'公開後に「Your site is live at ...」の「Visit site」から開いてください。'
               f'このURLは標準設定の候補であり、公開済みを保証しません。\n')
    target = os.environ.get('GITHUB_STEP_SUMMARY')
    if target:
        with open(target, 'a', encoding='utf-8') as out:
            out.write(summary)
    else:
        print(summary)
    print(f'OpenRank Portal Pages URL: {url}')


if __name__ == '__main__':
    main()
