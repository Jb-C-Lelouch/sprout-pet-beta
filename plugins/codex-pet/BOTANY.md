# 植物观察手记 · 资料与随机种子

查证日期：2026-09-15。文字为依据园艺机构与大学推广资料整理的短篇科普，随插件离线提供；没有复制或分发网站照片。

## 品种如何固定

自动播种完成时，从所在区域已解锁的种类中等概率随机选择一次，和种植记录一起提交。此前的走路、挖土计划不抽签。结果存入garden_plots.species，刷新、查看、浇水、施肥、移动、重启都读取同一结果。收获、收藏或明确移除之后重新种植才是新一轮随机；旧植物不重抽。

当前观赏区6种、菜畦4种，共10种；目标约20种，分批补充独立形态与资料。1级观赏区有白三叶和金盏花，菜畦有胡萝卜、小萝卜、生菜，初次种植就有多种可能。没有稀有度、付费抽取或保底机制。手动plant --plot N省略--plant或指定--plant random也使用随机种子；明确指定植物仍作为手动操作保留。

## 资料范围

“三叶草”以白三叶为原型，“薄荷”以留兰香为原型；“樱花”以Prunus serrulata为代表，不能将某个品种的花色或形状推广到所有樱花。植物卡分别说明简介、形态观察、生长习性与一个知识点。来源中的季节和气候信息有地域背景，未照搬为全国统一种植月份。

### 白三叶

Trifolium repens · 豆科 · 多年生草本

资料：[NC State Extension · 白三叶](https://plants.ces.ncsu.edu/plants/trifolium-repens/)。

### 留兰香（薄荷原型）

Mentha spicata · 唇形科 · 多年生草本

资料：[NC State Extension · 留兰香](https://plants.ces.ncsu.edu/plants/mentha-spicata/)。

### 雏菊

Bellis perennis · 菊科 · 多年生草本

资料：[RHS · 雏菊](https://www.rhs.org.uk/plants/94326/bellis-perennis/details)。

### 樱花（代表种）

Prunus serrulata · 蔷薇科 · 落叶乔木

资料：[Oregon State University · 樱花](https://landscapeplants.oregonstate.edu/plants/prunus-serrulata)。

### 胡萝卜

Daucus carota（栽培类型） · 伞形科 · 通常为二年生，栽培时多采收根

资料：[RHS · 胡萝卜栽培指南](https://www.rhs.org.uk/vegetables/carrots/grow-your-own)；[Garden Organic · 胡萝卜生命周期](https://www.gardenorganic.org.uk/expert-advice/how-to-grow/growing-guides/vegetables-herbs-guides/how-to-grow-carrot)。

### 番茄

Solanum lycopersicum · 茄科 · 草本作物

资料：[NC State Extension · 番茄](https://plants.ces.ncsu.edu/plants/solanum-lycopersicum/)。

胡萝卜的伞形科归属另参考[Kew胡萝卜资料](https://www.kew.org/plants/carrot)。

## 游戏与现实

游戏使用压缩的五阶段形象与经验进度，不等同于真实生长周期、比例或浇水施肥频率。像素形象是示意画，不作为现实植物鉴定依据。游戏白三叶调整为匍匐轮廓和三小叶，雏菊成熟形态增加基生叶丛；其余素材仍需持续提高形态细节。

点击植物打开独立的花园主题观察卡，阅读时暂停小芽动作，关闭后继续。卡片标注打开时的进度快照；点击资料按钮才打开外部网页。

## 本批新增植物

- 向日葵：Helianthus annuus；[RHS资料](https://www.rhs.org.uk/plants/105515/helianthus-annuus/details)。宽叶、顶端花蕾和黄色大花头。
- 金盏花：Calendula officinalis；[NC State Extension资料](https://plants.ces.ncsu.edu/plants/calendula-officinalis/)。较低株形、橙色花头。
- 小萝卜：Raphanus sativus，以夏季圆形红皮类型为原型；[RHS栽培指南](https://www.rhs.org.uk/vegetables/radishes/grow-your-own)。膨大部位渐显，不能把快速夏萝卜周期推广到冬萝卜。
- 生菜：Lactuca sativa；[RHS栽培指南](https://www.rhs.org.uk/vegetables/lettuce/grow-your-own)。层叠叶丛，游戏整株采收后补种；真实散叶类型可以多次摘叶。

所有10种资料提供简体中文和英文，科学名称、来源链接与存档品种ID共用。文字均随插件离线提供。装扮页切换语言后立即重绘并保存偏好，不重新抽取植物。
