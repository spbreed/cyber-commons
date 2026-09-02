# recordings/

Drop a lightboard recording here named after its curriculum session id and push
— the [publish-video workflow](../.github/workflows/publish-video.yml) uploads it
to YouTube, generates the title/description from that chapter's own
risk/control/lab text, and links it on the website.

```bash
cp ~/lightboard/a2.5-final.mp4 recordings/A2.5.mp4
git add recordings/A2.5.mp4 && git commit -m "record A2.5" && git push
```

Valid names are exactly the session ids in
[`site/data/curriculum.json`](../site/data/curriculum.json) — `M0.1.mp4`,
`A2.5.mp4`, `B2.2.mp4`, `E1.5.mp4` … Run `python3 scripts/link_video.py --list`
to see every id and which ones still need recording.

## Large files

Video is big and git is not. Two options:

1. **Recommended — don't commit the video at all.** Upload it however you
   normally do, then just register the id:
   ```bash
   python3 scripts/link_video.py --session A2.5 --youtube-id <id>
   ```
   Or run the workflow manually (Actions → Publish lightboard recording) with a
   `youtube_id` and no file.

2. **Commit it via [Git LFS](https://git-lfs.com)** if you want the source of
   truth in the repo:
   ```bash
   git lfs install && git lfs track "recordings/*.mp4"
   git add .gitattributes
   ```

Either way the chapter ends up with a ▶ Watch link; option 1 keeps the repo small.
