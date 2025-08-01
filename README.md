# Gelbooru Tag Pruner

统计 Gelbooru 上 20000 条投稿的 tags，通过 GPT-4o 对 tags 进行分类，之后通过脚本去除特定种类的 tags

已有统计分类（AI分类，可能存在误差）：

- body_part.json  
- character.json  
- character_tags_sorted_nonsexual.json  
- dress.json  
- poses.json  
- sexual.json

## 一般流程
1. 清除分类 Tag
2. 根据词频细筛