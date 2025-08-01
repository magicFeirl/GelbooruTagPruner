import asyncio
import aiofiles
import glob
import os
import json


class TagInfo(dict):
    def __init__(self, *args):
        super().__init__(self, *args)
        self.file_path = ''
        self.tags = []
        self.pruned_tags = []

    @classmethod
    def create(cls, params):
        info = TagInfo()

        for key in ['file_path', 'tags', 'pruned_tags']:
            if key in params:
                setattr(info, key, params[key])
        
        return info
                
class TagPruner(object):
    def __init__(self, path):
        self.path = path
        self.result = []

    def _normalize_tag(self, tags: str):
        def remove_underline(tag):
            return tag.strip().replace("_", " ")

        return [remove_underline(tag) for tag in tags.split(",")]

    async def read(self, concurrency=2, ext=".txt"):
        """
        并发读取 tag 文件
        """

        async def worker(file_path, sem):
            async with sem:
                async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                    tags = await f.read()

                    return TagInfo.create({"file_path": file_path, "tags": self._normalize_tag(tags), 'pruned_tags': []})

        tasks = []
        sem = asyncio.Semaphore(concurrency)
        for file_path in glob.glob(os.path.join(self.path, f"*{ext}")):
            tasks.append(asyncio.create_task(worker(file_path, sem)))

        return await asyncio.gather(*tasks)

    def read_classification(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def prune_one(self, info, tag_dict, eq=True):
        tags_list = info["tags"]

        def isPrune(tag):
            if eq:
                return tag not in tag_dict
            else:
                return tag in tag_dict

        pruned_tags = [tag for tag in tags_list if isPrune(tag)]

        return TagInfo.create({**info, "pruned_tags": pruned_tags})

    async def prune(self, classification, concurrency=2, ext=".txt", eq=True):
        """清除符合分类的 Tag
        :param: eq: True 删除匹配的 tag；False 删除不匹配的 tag
        """
        info = await self.read(concurrency, ext)
        tag_dict = self.read_classification(classification)

        self.result = []
        for item in info:
            self.result.append(self.prune_one(item, tag_dict, eq))

        return self.result

    async def save(self, bak = True):
        for info in self.result:
            async with aiofiles.open(info.file_path, 'w', encoding='utf-8') as f:
                f.write(', '.join(info.pruned_tags))

            if bak:
                basename = os.path.basename(info.file_path)
                async with aiofiles.open(f'{basename}_0', 'w', encoding='utf-8') as f:
                    f.write(', '.join(info.tags))
                    

async def main():
    pass


if __name__ == "__main__":
    main()
