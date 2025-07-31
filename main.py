import asyncio
import aiofiles
import glob
import os
import json


class TagPruner(object):
    def __init__(self, path):
        self.path = path
        self.result = []

    def _normalize_tag(self, tag: str):
        return tag.strip().replace("_", " ")

    async def read(self, concurrency=2, ext=".txt"):
        """
        并发读取 tag 文件
        """

        async def worker(file_path, sem):
            async with sem:
                async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                    tags = await f.read()

                    return {
                        "file_path": file_path,
                        "tags": [self._normalize_tag(tag) for tag in tags.split(",")],
                    }

        tasks = []
        sem = asyncio.Semaphore(concurrency)
        for file_path in glob(os.path.join(self.path, f"*{ext}")):
            tasks.append(asyncio.create_task(worker(file_path, sem)))

        return await asyncio.gather(*tasks)

    async def prune(self, classification, concurrency=2, ext=".txt"):
        info = self.read(concurrency, ext)

        async with aiofiles.open(classification, "r", encoding="utf-8") as f:
            tag_dict = json.load(f)

        self.result = []
        for item in info:
            tags_list = item["tags"]
            pruned_tags = [
                tag for tags in tags_list for tag in tags if tag not in tag_dict
            ]

            data = { **item, 'pruned_tags': pruned_tags}
            self.result.append(data)

        return self.result
    

async def main():
    pass


if __name__ == "__main__":
    main()
