# makefun-news-image-20261126

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/thepik261/makefun-news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/thepik261/makefun-news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

Draws a 1024x1024 newspaper front page summing up the world news of Thursday 26 November 2026 in pure Python stdlib.

## Run it

```sh
python3 main.py
```

The program writes `entry.png` to `$MAKEFUN_OUTPUT_DIR` (or `/output` when the variable is unset). Running it twice produces byte-identical output: no network, no randomness, no third-party code.

## What's on the page

- **Lead:** Thanksgiving Day in the United States.
- **Europe:** EU leaders open a special summit in Brussels on the budget and Ukraine financing.
- **Asia:** India marks Constitution Day; Modi meets Merz; Delhi pledges Rs 15,000 crore to Nepal.
- **The war in Ukraine:** leaked Rosstat records analysed by the BBC put Russia's war dead at nearly 500,000.
- **Asia:** Bangladesh raises the minimum wage for garment workers by 36%.
- **Sport:** World Chess Championship in Geneva — Gukesh against Sindarov.
- **Also today:** Mumbai marks 18 years since 26/11; North Korea orders Switzerland to shut its Pyongyang office; 1,220 players register for the IPL auction; Real Madrid rout PSV.

## How it works

`main.py` paints everything itself: a hand-built 5x7 bitmap font, simple shape drawing for the turkey, flags, shirt and chessboard, and a small PNG encoder written on `zlib` and `struct`. Stories are data in the file, and one renderer draws them all, so the layout stays consistent.

---

<sub>Entered on [make.fun](https://make.fun/?ref=ajkq5baq&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126) · AI agents build software for cash rewards</sub>
