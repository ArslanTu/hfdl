# What's this?

A simple tool for download hf repo on any machin with `wget` command.

# How to run

## common way

With all requirements installed: `python -m src.main`

## vercel

Fork this repo and deploy with vercel.

# How to use

`wget --no-proxy -O - 'http://127.0.0.1:8000/?hf_path=Qwen%2FQwen1.5-14B-Chat' | bash`

# TODO

- [x] support vercel deploy
- [ ] support resume download
- [ ] perf improvement