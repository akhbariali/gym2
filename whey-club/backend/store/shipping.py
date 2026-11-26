# Quoted prepaid express-post tariffs in tomans, using packed weight.
PROVINCIAL_CAPITALS=set('تهران|کرج|قم|قزوین|رشت|ساری|گرگان|اردبیل|تبریز|ارومیه|زنجان|سنندج|همدان|کرمانشاه|ایلام|خرم آباد|اراک|اصفهان|شهرکرد|یاسوج|اهواز|شیراز|بوشهر|بندرعباس|کرمان|یزد|سمنان|مشهد|بجنورد|بیرجند|زاهدان'.split('|'))

def postage(method,city,weights):
    if method=='tipax':return 0
    if method!='post':raise ValueError('روش ارسال معتبر نیست.')
    if any(not weight for weight,quantity in weights):raise ValueError('وزن ارسال محصول هنوز مشخص نشده است؛ تیپاکس را انتخاب کنید.')
    weight=sum(weight*quantity for weight,quantity in weights)
    if weight<1000:
        city=' '.join(city.replace('\u200c',' ').split())
        return 220000 if city in PROVINCIAL_CAPITALS else 200000
    for limit,fee in [(2000,250000),(3000,330000),(4000,400000),(5000,470000),(6000,550000),(7000,610000)]:
        if weight<limit:return fee
    raise ValueError('برای بسته ۷ کیلوگرم یا بیشتر تیپاکس را انتخاب کنید.')
