"""Short, sourced botanical notes, bundled for offline reading. Checked 2026-09-14."""
PROFILES={
 'clover':dict(name='白三叶',latin='Trifolium repens',family='豆科',life='多年生草本',
  intro='这里的“三叶草”以白三叶为原型。它贴近地面匍匐生长，茎的节处可以生根，逐渐铺成一小片绿毯。',
  observe='一片复叶通常由三枚小叶组成；白色的圆花头其实聚集了许多小花。',
  habitat='喜欢湿润土壤，适合阳光充足或半阴处。它会向周围蔓延，并不是一根高高的直立花茎。',
  fact='“三叶”说的是复叶上的小叶数，不是整株只有三片叶子。',
  source='NC State Extension · 白三叶',url='https://plants.ces.ncsu.edu/plants/trifolium-repens/'),
 'mint':dict(name='留兰香（薄荷原型）',latin='Mentha spicata',family='唇形科',life='多年生草本',
  intro='薄荷不是只有一种。本游戏采用留兰香作为原型：它有明显香气，也会通过地下根茎向周围扩展。',
  observe='叶片对生、边缘有锯齿；茎的横截面近方形。开花时，许多小花聚集在茎顶的穗状花序上。',
  habitat='喜欢湿润而排水良好的土壤，可在全日照或半阴处生长；干燥土壤不适合它。',
  fact='把它种在容器里可以帮助限制蔓延；现实里浇水要看土壤，不是越多越好。',
  source='NC State Extension · 留兰香',url='https://plants.ces.ncsu.edu/plants/mentha-spicata/'),
 'daisy':dict(name='雏菊',latin='Bellis perennis',family='菊科',life='多年生草本',
  intro='雏菊是一种低矮的多年生草本。叶片从基部聚成莲座状，花头有黄色中心，外围常见白色或带粉色的花瓣状部分。',
  observe='注意贴近地面的匙形叶片，以及从叶丛中伸出的花梗；它不是高大的分枝灌木。',
  habitat='适合阳光充足或半阴处，土壤需要排水良好。园艺品种的花色和花形可以不同。',
  fact='资料中的“多年生”描述寿命，不表示在游戏里成熟后会永远保持同一朵花。',
  source='RHS · 雏菊',url='https://www.rhs.org.uk/plants/94326/bellis-perennis/details'),
 'cherry':dict(name='樱花（代表种）',latin='Prunus serrulata',family='蔷薇科',life='落叶乔木',
  intro='“樱花”包含多种植物和园艺品种。这张卡以Prunus serrulata为代表，介绍一类春季观花的落叶树。',
  observe='叶片互生，边缘有锯齿；树皮可见横向皮孔。不同园艺品种的花色、花瓣层数和树形会有差异。',
  habitat='适合阳光充足或半阴处。现实里会经历生长、落叶等季节变化，花期并非全年。',
  fact='粉色树冠是游戏的概括画法，不代表所有樱花都开粉色重瓣花。',
  source='Oregon State University · 樱花',url='https://landscapeplants.oregonstate.edu/plants/prunus-serrulata'),
 'carrot':dict(name='胡萝卜',latin='Daucus carota（栽培类型）',family='伞形科',life='通常为二年生，栽培时多采收根',
  intro='我们通常采收的是胡萝卜膨大的根。不同栽培品种不仅有橙色，也有紫色、白色和黄色。',
  observe='根主要在土里形成；地上长出的叶片并不是它的橙色可收获部分。',
  habitat='喜欢阳光和疏松、排水良好的土壤；石块或板结土壤可能让根分叉、形状不规则。通常直接播种，避免移栽伤根。',
  fact='RHS给出的常见采收参考约为播后12–16周，小胡萝卜可更早；实际取决于品种、天气和目标大小。',
  source='RHS · 胡萝卜栽培指南',url='https://www.rhs.org.uk/vegetables/carrots/grow-your-own',
  extra_source='Garden Organic · 胡萝卜生命周期',extra_url='https://www.gardenorganic.org.uk/expert-advice/how-to-grow/growing-guides/vegetables-herbs-guides/how-to-grow-carrot'),
 'tomato':dict(name='番茄',latin='Solanum lycopersicum',family='茄科',life='草本作物',
  intro='番茄开黄色星形小花，随后形成果实。不同品种的果实大小、形状和颜色差异很大，成熟时不一定都是红色。',
  observe='观察花朵、未熟果与成熟果的变化；叶片分裂成小叶，茎叶表面有毛。',
  habitat='需要充足阳光，以及湿润、排水良好的土壤。不同品种的株形不同，有的会向四周伸展。',
  fact='从植物学的果实分类看，番茄属于浆果；生活中把它归为蔬菜，是另一种分类方式。',
  source='NC State Extension · 番茄',url='https://plants.ces.ncsu.edu/plants/solanum-lycopersicum/'),
}

GAME_NOTE='游戏使用压缩的五阶段形象与经验进度，不等同于真实生长周期、比例或浇水施肥频率。'

PROFILES.update({
 'sunflower':dict(name='向日葵',latin='Helianthus annuus',family='菊科',life='一年生草本',intro='高大的茎托起黄色花头，中心呈深褐色。不同栽培品种的高度和花头大小差异很大。',observe='叶片宽大，呈卵形至心形，表面粗糙有毛。观察从顶端花蕾到黄色花头展开的变化。',habitat='喜欢充足阳光和湿润、排水良好的土壤。高大的植株可能需要支撑。',fact='花朵吸引蜜蜂，结出的种子还可以为雀类鸟儿提供食物。',source='RHS · 向日葵',url='https://www.rhs.org.uk/plants/105515/helianthus-annuus/details'),
 'calendula':dict(name='金盏花',latin='Calendula officinalis',family='菊科',life='一年生草本',intro='金盏花常见黄色或橙色花头，株形较紧凑。这里用橙色花头表现它，与白色雏菊区分。',observe='叶片长圆至披针形，花头可以是单瓣或重瓣。游戏画的是其中一种简化形态。',habitat='适合阳光充足、排水良好的地方；酷热或干旱时表现较差，炎热夏季可稍遮阴。',fact='及时去掉开败的花头有助于继续开花；它也可能在花园里自行播种。',source='NC State Extension · 金盏花',url='https://plants.ces.ncsu.edu/plants/calendula-officinalis/'),
 'radish':dict(name='小萝卜',latin='Raphanus sativus',family='十字花科',life='根菜作物',intro='这里以圆形红皮的小萝卜为原型。萝卜的栽培类型很多，并不都是小圆球。',observe='叶丛下方的膨大部分是采收重点。游戏露出红色根肩来提示进度，实际大部分长在土里。',habitat='喜欢湿润的土壤，缺水会影响口感。及时采收比一味等待长大更合适。',fact='RHS介绍的快速夏萝卜约四周即可采收；冬萝卜所需时间更长，不能一概而论。',source='RHS · 萝卜栽培指南',url='https://www.rhs.org.uk/vegetables/radishes/grow-your-own'),
 'lettuce':dict(name='生菜',latin='Lactuca sativa',family='菊科',life='叶菜作物',intro='生菜既有结球类型，也有松散的叶用类型。游戏采用叶丛展开的形态，成熟不需要等到开花。',observe='从几片小叶逐渐长成层叠叶丛。采收的是叶片，与番茄采收果实不同。',habitat='适合保湿而肥沃的土壤。炎热时适当遮阴；高温、干燥容易促使抽薹。',fact='部分散叶生菜可以陆续摘取外叶，多次采收。游戏目前统一按整株收获后重新播种处理。',source='RHS · 生菜栽培指南',url='https://www.rhs.org.uk/vegetables/lettuce/grow-your-own'),
})

# Stable species IDs and scientific names are shared by both languages.
EN={
 'clover':('White clover','Fabaceae','Herbaceous perennial','A low, creeping plant. Its stems root at the nodes and gradually form a green carpet.','A compound leaf usually has three leaflets. Each round white flower head contains many small flowers.','Grows in moist soil in sun or partial shade, spreading close to the ground.','Three refers to leaflets in one compound leaf, not the total leaves on the plant.'),
 'mint':('Spearmint','Lamiaceae','Herbaceous perennial','This garden uses spearmint as its mint model. Aromatic shoots spread through underground rhizomes.','Look for paired, toothed leaves, square stems and small flowers clustered in spikes.','Prefers moist, well-drained soil in sun or partial shade. Dry soil does not suit it.','Growing mint in a container helps limit its spread. Water according to the soil, not a fixed game timer.'),
 'daisy':('Common daisy','Asteraceae','Herbaceous perennial','A low perennial with a basal leaf rosette and yellow-centred heads edged in white or pink.','Spoon-shaped leaves hug the ground. Flower stalks rise above the rosette.','Grows in sun or partial shade with good drainage. Cultivars vary in flower colour and form.','Perennial describes its lifespan; an individual flower does not stay open forever.'),
 'cherry':('Japanese flowering cherry','Rosaceae','Deciduous tree','Flowering cherries include many species and cultivars. This card uses Prunus serrulata as a representative.','Look for alternate, toothed leaves and horizontal marks on the bark. Flower form varies by cultivar.','Grows in sun or partial shade. Real trees shed leaves and flower seasonally, not all year.','The pink canopy is a game shorthand. Not every flowering cherry has double pink flowers.'),
 'carrot':('Carrot','Apiaceae','Usually biennial; grown for its root','Carrots are grown for swollen roots. Cultivars can be orange, purple, white or yellow.','The root develops mainly underground. The green leaves are separate from the orange harvest.','Needs loose, well-drained soil and sun. Stones or compacted soil can cause misshapen roots.','RHS gives about 12–16 weeks as a common harvest guide; baby carrots can be picked earlier.'),
 'tomato':('Tomato','Solanaceae','Herbaceous crop','Yellow star-shaped flowers develop into fruits. Ripe fruits vary in size, shape and colour.','Watch flowers become green fruit, then ripe fruit. Stems and divided leaves bear hairs.','Needs plenty of sunlight and moist, well-drained soil. Growth habit varies among cultivars.','Botanically, a tomato is a berry. Calling it a vegetable in cooking uses a different classification.'),
 'sunflower':('Sunflower','Asteraceae','Annual','Tall stems carry yellow heads with dark centres. Height and flower size vary among cultivars.','Broad oval to heart-shaped leaves feel rough and hairy. Watch the top bud open into a flower head.','Needs full sun and moist, well-drained soil. Tall plants may need support.','Flowers attract bees; the seeds that follow provide food for finches.'),
 'calendula':('Pot marigold','Asteraceae','Annual','Calendula bears yellow or orange heads. This game uses orange flowers to distinguish it from the daisy.','Leaves are oblong to lance-shaped. Flower heads can be single or double.','Likes sun and good drainage. Heat and drought can reduce performance; light summer shade can help.','Removing spent flower heads encourages more flowers. It can also self-seed in the garden.'),
 'radish':('Radish','Brassicaceae','Root crop','This garden models a small, round, red-skinned radish. Other cultivars have very different shapes.','The swollen part below the leaves is harvested. The game exposes its shoulder to show progress.','Keep soil moist and harvest promptly. Dry conditions can reduce eating quality.','Fast summer radishes can be ready in about four weeks. Winter types take longer.'),
 'lettuce':('Lettuce','Asteraceae','Leaf crop','Lettuce includes heading and loose-leaf types. This garden models an expanding rosette, harvested before flowering.','Small leaves build into a layered rosette. The harvest is leaves, rather than fruit as in tomatoes.','Likes fertile, moisture-retentive soil. Summer shade can help; hot, dry conditions encourage bolting.','Some loose-leaf types allow repeated picking. The game currently harvests the whole plant and sows again.'),
}


def profile(species,language='zh'):
    result=dict(PROFILES[species])
    if language=='en':
        result.update(zip(('name','family','life','intro','observe','habitat','fact'),EN[species]))
        result['latin']=result['latin'].replace('（栽培类型）',' (cultivated forms)')
        result['source']=result['source'].split(' · ')[0]
    return result


def name(species,language='zh'):
    return profile(species,language)['name']
