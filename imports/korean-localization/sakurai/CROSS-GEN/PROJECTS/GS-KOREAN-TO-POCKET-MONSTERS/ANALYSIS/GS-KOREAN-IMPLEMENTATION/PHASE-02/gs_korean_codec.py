#!/usr/bin/env python3
"""Codec and lossless Bank 6C extractor for official Korean Gold/Silver.

The Hangul labels were independently tied to ROM glyph slots and cross-checked
against Narishma-gb/pokegold-kr's public charmap source. ROM bytes remain the
authority for occupied code slots and every round-trip assertion.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


BANK_SIZE = 0x4000
BANK_6C = 0x6C
FONT_FIRST_BANK = 0x78
FONT_LAST_BANK = 0x7A
TERMINATOR = 0x50

# Unicode labels in ascending occupied ROM code order for tables 01-0A.
# The positions themselves are derived from nonblank ROM glyph tiles.
HANGUL_SEQUENCE = (
    "가각간갇갈갉갊감갑값갓갔강갖갗같갚갛개객갠갤갬갭갯갰갱갸갹갼걀걋걍걔걘걜거걱건걷걸걺검겁것겄겅겆겉겊겋게겐겔겜겝겟겠겡겨격겪견겯결겹겸겻겼경곁계곈곌곕곗고곡곤곧골곪곬곯곰곱곳공곶과곽관괄괆괌괍괏광괘괜"
    "괠괩괬괭괴괵괸괼괻굅굇굉교굔굘굡굣구국군굳굴굵굶굻굼굽굿궁궂궈궉권궐궜궝궤궷귀귁귄귈귐귑귓규균귤그극근귿글긁금급긋긍긔기긱긴긷길긺김깁깃깅깆깊까깍깎깐깔깖깜깝깟깠깡깥깨깩깬깰깸깹깻깼깽꺄꺅꺌꺼꺽꺾껀껄"
    "껌껍껏껐껑께껙껜껨껫껭껴껸껼꼇꼈꼍꼐꼬꼭꼰꼲꼴꼼꼽꼿꽁꽂꽃꽈꽉꽐꽜꽝꽤꽥꽹꾀꾄꾈꾐꾑꾕꾜꾸꾹꾼꿀꿇꿈꿉꿋꿍꿎꿔꿜꿨꿩꿰꿱꿴꿸뀀뀁뀄뀌뀐뀔뀜뀝뀨끄끅끈끊끌끎끓끔끕끗끙끝끼끽낀낄낌낍낏낑나낙낚난낟날낡낢남"
    "납낫났낭낮낯낱낳내낵낸낼냄냅냇냈냉냐냑냔냘냠냥너넉넋넌널넒넓넘넙넛넜넝넣네넥넨넬넴넵넷넸넹녀녁년녈념녑녔녕녘녜녠노녹논놀놂놈놉놋농높놓놔놘놜놨뇌뇐뇔뇜뇝뇟뇨뇩뇬뇰뇹뇻뇽누눅눈눋눌눔눕눗눙눠눴눼뉘뉜뉠뉨"
    "뉩뉴뉵뉼늄늅늉느늑는늘늙늚늠늡늣능늦늪늬늰늴니닉닌닐닒님닙닛닝닢다닥닦단닫달닭닮닯닳담답닷닸당닺닻닿대댁댄댈댐댑댓댔댕더덕덖던덛덜덞덟덤덥덧덩덫덮데덱덴델뎀뎁뎃뎄뎅뎌뎐뎔뎠뎡뎨뎬도독돈돋돌돎돔돕돗동돛"
    "돝돠돤돨돼됐되된될됨됩됫됴두둑둔둘둠둡둣둥둬뒀뒈뒝뒤뒨뒬뒵뒷뒹듀듄듈듐듕드득든듣들듦듬듭듯등듸디딕딘딛딜딤딥딧딨딩딪따딱딴딸땀땁땃땄땅땋때땍땐땔땜땝땟땠땡떠떡떤떨떪떫떰떱떳떴떵떻떼떽뗀뗄뗌뗍뗏뗐뗑뗘뗬"
    "또똑똔똘똥똬똴뙈뙤뙨뚜뚝뚠뚤뚫뚬뚱뛔뛰뛴뛸뜀뜁뜅뜨뜩뜬뜯뜰뜸뜹뜻띄띈띌띔띕띠띤띨띰띱띳띵라락란랄람랍랏랐랑랒랖랗뢔래랙랜랠램랩랫랬랭랴략랸럇량러럭런럴럼럽럿렀렁렇레렉렌렐렘렙렛렝려력련렬렴렵렷렸령례롄"
    "롑롓로록론롤롬롭롯롱롸롼뢍뢨뢰뢴뢸룀룁룃룅료룐룔룝룟룡루룩룬룰룸룹룻룽뤄뤘뤠뤼뤽륀륄륌륏륑류륙륜률륨륩륫륭르륵른를름릅릇릉릊릍릎리릭린릴림립릿링마막만많맏말맑맒맘맙맛망맞맡맣매맥맨맬맴맵맷맸맹맺먀먁먈"
    "먕머먹먼멀멂멈멉멋멍멎멓메멕멘멜멤멥멧멨멩며멱면멸몃몄명몇몌모목몫몬몰몲몸몹못몽뫄뫈뫘뫙뫼묀묄묍묏묑묘묜묠묩묫무묵묶문묻물묽묾뭄뭅뭇뭉뭍뭏뭐뭔뭘뭡뭣뭬뮈뮌뮐뮤뮨뮬뮴뮷므믄믈믐믓미믹민믿밀밂밈밉밋밌밍및"
    "밑바박밖밗반받발밝밞밟밤밥밧방밭배백밴밸뱀뱁뱃뱄뱅뱉뱌뱍뱐뱝버벅번벋벌벎범법벗벙벚베벡벤벧벨벰벱벳벴벵벼벽변별볍볏볐병볕볘볜보복볶본볼봄봅봇봉봐봔봤봬뵀뵈뵉뵌뵐뵘뵙뵤뵨부북분붇불붉붊붐붑붓붕붙붚붜붤붰"
    "붸뷔뷕뷘뷜뷩뷰뷴뷸븀븃븅브븍븐블븜븝븟비빅빈빌빎빔빕빗빙빚빛빠빡빤빨빪빰빱빳빴빵빻빼빽뺀뺄뺌뺍뺏뺐뺑뺘뺙뺨뻐뻑뻔뻗뻘뻠뻣뻤뻥뻬뼁뼈뼉뼘뼙뼛뼜뼝뽀뽁뽄뽈뽐뽑뽕뾔뾰뿅뿌뿍뿐뿔뿜뿟뿡쀼쁑쁘쁜쁠쁨쁩삐삑삔삘삠"
    "삡삣삥사삭삯산삳살삵삶삼삽삿샀상샅새색샌샐샘샙샛샜생샤샥샨샬샴샵샷샹섀섄섈섐섕서석섞섟선섣설섦섧섬섭섯섰성섶세섹센셀셈셉셋셌셍셔셕션셜셤셥셧셨셩셰셴셸솅소속솎손솔솖솜솝솟송솥솨솩솬솰솽쇄쇈쇌쇔쇗쇘쇠쇤"
    "쇨쇰쇱쇳쇼쇽숀숄숌숍숏숑수숙순숟술숨숩숫숭쌰쎼숯숱숲숴쉈쉐쉑쉔쉘쉠쉥쉬쉭쉰쉴쉼쉽쉿슁슈슉슐슘슛슝스슥슨슬슭슴습슷승시식신싣실싫심십싯싱싶싸싹싻싼쌀쌈쌉쌌쌍쌓쌔쌕쌘쌜쌤쌥쌨쌩썅써썩썬썰썲썸썹썼썽쎄쎈쎌쏀"
    "쏘쏙쏜쏟쏠쏢쏨쏩쏭쏴쏵쏸쐈쐐쐤쐬쐰쓔쐴쐼쐽쑈쑤쑥쑨쑬쑴쑵쑹쒀쒔쒜쒸쒼쓩쓰쓱쓴쓸쓺쓿씀씁씌씐씔씜씨씩씬씰씸씹씻씽아악안앉않알앍앎앓암압앗았앙앝앞애액앤앨앰앱앳앴앵야약얀얄얇얌얍얏양얕얗얘얜얠얩어억언얹얻"
    "얼얽얾엄업없엇었엉엊엌엎에엑엔엘엠엡엣엥여역엮연열엶엷염엽엾엿였영옅옆옇예옌옐옘옙옛옜오옥온올옭옮옰옳옴옵옷옹옻와왁완왈왐왑왓왔왕왜왝왠왬왯왱외왹왼욀욈욉욋욍요욕욘욜욤욥욧용우욱운울욹욺움웁웃웅워웍원"
    "월웜웝웠웡웨웩웬웰웸웹웽위윅윈윌윔윕윗윙유육윤율윰윱윳융윷으윽은을읆음읍읏응읒읓읔읕읖읗의읜읠읨읫이익인일읽읾잃임입잇있잉잊잎자작잔잖잗잘잚잠잡잣잤장잦재잭잰잴잼잽잿쟀쟁쟈쟉쟌쟎쟐쟘쟝쟤쟨쟬저적전절젊"
    "점접젓정젖제젝젠젤젬젭젯젱져젼졀졈졉졌졍졔조족존졸졺좀좁좃종좆좇좋좌좍좔좝좟좡좨좼좽죄죈죌죔죕죗죙죠죡죤죵주죽준줄줅줆줌줍줏중줘줬줴쥐쥑쥔쥘쥠쥡쥣쥬쥰쥴쥼즈즉즌즐즘즙즛증지직진짇질짊짐집짓쬬징짖짙짚짜"
    "짝짠짢짤짧짬짭짯짰짱째짹짼쨀쨈쨉쨋쨌쨍쨔쨘쨩쩌쩍쩐쩔쩜쩝쩟쩠쩡쩨쩽쪄쪘쪼쪽쫀쫄쫌쫍쫏쫑쫓쫘쫙쫠쫬쫴쬈쬐쬔쬘쬠쬡쭁쭈쭉쭌쭐쭘쭙쭝쭤쭸쭹쮜쮸쯔쯤쯧쯩찌찍찐찔찜찝찡찢찧차착찬찮찰참찹찻찼창찾채책챈챌챔챕챗챘"
    "챙챠챤챦챨챰챵처척천철첨첩첫첬청체첵첸첼쳄쳅쳇쳉쳐쳔쳤쳬쳰촁초촉촌촐촘촙촛총촤촨촬촹최쵠쵤쵬쵭쵯쵱쵸춈추축춘출춤춥춧충춰췄췌췐취췬췰췸췹췻췽츄츈츌츔츙츠측츤츨츰츱츳층치칙친칟칠칡침칩칫칭카칵칸칼캄캅캇"
    "캉캐캑캔캘캠캡캣캤캥캬캭컁커컥컨컫컬컴컵컷컸컹케켁켄켈켐켑켓켕켜켠켤켬켭켯켰켱켸코콕콘콜콤콥콧콩콰콱콴콸쾀쾅쾌쾡쾨쾰쿄쿠쿡쿤쿨쿰쿱쿳쿵쿼퀀퀄퀑퀘퀭퀴퀵퀸퀼큄큅큇큉큐큔큘큠크큭큰클큼큽킁키킥킨킬킴킵킷킹"
    "타탁탄탈탉탐탑탓탔탕태택탠탤탬탭탯탰탱탸턍터턱턴털턺텀텁텃텄텅테텍텐텔템텝텟텡텨텬텼톄톈토톡톤톨톰톱톳통톺톼퇀퇘퇴퇸툇툉툐투툭툰툴툼툽툿퉁퉈퉜퉤튀튁튄튈튐튑튕튜튠튤튬튱트특튼튿틀틂틈틉틋틔틘틜틤틥티틱"
    "틴틸팀팁팃팅파팍팎판팔팖팜팝팟팠팡팥패팩팬팰팸팹팻팼팽퍄퍅퍼퍽펀펄펌펍펏펐펑페펙펜펠펨펩펫펭펴편펼폄폅폈평폐폘폡폣포폭폰폴폼폽폿퐁퐈퐝푀푄표푠푤푭푯푸푹푼푿풀풂품풉풋풍풔풩퓌퓐퓔퓜퓟퓨퓬퓰퓸퓻퓽프픈플"
    "픔픕픗피픽핀필핌핍핏핑하학한할핥함합핫항해핵핸핼햄햅햇했행햐향허헉헌헐헒험헙헛헝헤헥헨헬헴헵헷헹혀혁현혈혐협혓혔형혜혠혤혭호혹혼홀홅홈홉홋홍홑화확환활홧황홰홱홴횃횅회획횐횔횝횟횡효횬횰횹횻후훅훈훌훑훔"
    "훗훙훠훤훨훰훵훼훽휀휄휑휘휙휜휠휨휩휫휭휴휵휸휼흄흇흉흐흑흔흖흗흘흙흠흡흣흥흩희흰흴흼흽힁히힉힌힐힘힙힛힝"
)

# Table 0B: compatibility/input symbols. <SP> is intentionally a blank glyph.
TABLE_B_MAP = {
    0x00: "<ㄱ>",
    0x01: "<ㄴ>",
    0x02: "<ㄷ>",
    0x03: "<ㄹ>",
    0x04: "<ㅁ>",
    0x05: "<ㅂ>",
    0x06: "<ㅅ>",
    0x07: "<ㅇ>",
    0x08: "<ㅈ>",
    0x09: "<ㅊ>",
    0x0A: "<ㅋ>",
    0x0B: "<ㅌ>",
    0x0C: "<ㅍ>",
    0x0D: "<ㅎ>",
    0x0E: "<ㄲ>",
    0x0F: "<ㄸ>",
    0x10: "<ㅃ>",
    0x11: "<ㅆ>",
    0x12: "<ㅉ>",
    0x20: "<ㅏ>",
    0x21: "<ㅑ>",
    0x22: "<ㅓ>",
    0x23: "<ㅕ>",
    0x24: "<ㅗ>",
    0x25: "<ㅛ>",
    0x26: "<ㅜ>",
    0x27: "<ㅠ>",
    0x28: "<ㅡ>",
    0x29: "<ㅣ>",
    0x2A: "<ㅐ>",
    0x2B: "<ㅒ>",
    0x2C: "<ㅔ>",
    0x2D: "<ㅖ>",
    0x2E: "<ㅘ>",
    0x2F: "<ㅙ>",
    0x30: "<ㅚ>",
    0x31: "<ㅝ>",
    0x32: "<ㅞ>",
    0x33: "<ㅟ>",
    0x34: "<ㅢ>",
    0x3E: "<_>",
    0x3F: "<—>",
    0x60: "「",
    0x61: "」",
    0x62: "『",
    0x63: "』",
    0x64: "(",
    0x65: ")",
    0x66: "!",
    0x67: "?",
    0x68: "-",
    0x69: "~",
    0x6A: "…",
    0x6B: ",",
    0x6C: "<.>",
    0xF0: "<0>",
    0xF1: "<1>",
    0xF2: "<2>",
    0xF3: "<3>",
    0xF4: "<4>",
    0xF5: "<5>",
    0xF6: "<6>",
    0xF7: "<7>",
    0xF8: "<8>",
    0xF9: "<9>",
    0xFF: "<SP>",
}

# Single-byte decoding preference for the normal Korean text context.
# Literal characters: 177; symbolic/control tokens: 65.
SINGLE_BYTE_MAP = {
    0x00: "<NULL>",
    0x0C: "ガ",
    0x0D: "ギ",
    0x0E: "グ",
    0x0F: "ゲ",
    0x10: "ゴ",
    0x11: "ザ",
    0x12: "ジ",
    0x13: "ズ",
    0x14: "ゼ",
    0x15: "ゾ",
    0x16: "ダ",
    0x17: "ヂ",
    0x18: "ヅ",
    0x19: "デ",
    0x1A: "ド",
    0x1D: "<BSP>",
    0x1E: "<LF>",
    0x1F: "<KOUGEKI>",
    0x20: "バ",
    0x21: "ビ",
    0x22: "ブ",
    0x23: "ボ",
    0x24: "が",
    0x25: "ぎ",
    0x26: "ぐ",
    0x27: "げ",
    0x28: "ご",
    0x29: "ざ",
    0x2A: "じ",
    0x2B: "ず",
    0x2C: "ぜ",
    0x2D: "ぞ",
    0x2E: "だ",
    0x2F: "ぢ",
    0x30: "づ",
    0x31: "で",
    0x32: "ど",
    0x33: "<POKE>",
    0x34: "<WBR>",
    0x35: "<ROUTE>",
    0x36: "<WATASHI>",
    0x37: "<KOKO_WA>",
    0x38: "ば",
    0x39: "び",
    0x3A: "ぶ",
    0x3B: "ベ",
    0x3C: "ぼ",
    0x3D: "パ",
    0x3E: "ピ",
    0x3F: "⁂",
    0x40: "ポ",
    0x41: "ぱ",
    0x42: "ぴ",
    0x43: "ぷ",
    0x44: "ペ",
    0x45: "ぽ",
    0x46: "<PKMN>",
    0x47: "#",
    0x48: "<……>",
    0x49: "<PC>",
    0x4A: "<TM>",
    0x4B: "<ROCKET>",
    0x4C: "<DEXEND>",
    0x4D: "<RED>",
    0x4E: "<GREEN>",
    0x4F: "<ENEMY>",
    0x50: "@",
    0x51: "<PLAYER>",
    0x52: "<RIVAL>",
    0x53: "<TARGET>",
    0x54: "<USER>",
    0x55: "<TRAINER>",
    0x56: "<_CONT>",
    0x57: "<SCROLL>",
    0x59: "<NEXT>",
    0x5A: "<LINE>",
    0x5B: "<MOM>",
    0x5C: "<PARA>",
    0x5D: "<CONT>",
    0x5E: "<m>",
    0x5F: "<k>",
    0x60: "■",
    0x61: "▲",
    0x62: "☎",
    0x63: "<BOLD_D>",
    0x64: "<BOLD_E>",
    0x65: "<BOLD_F>",
    0x66: "<BOLD_G>",
    0x67: "<BOLD_H>",
    0x68: "<BOLD_I>",
    0x69: "<BOLD_V>",
    0x6A: "<BOLD_S>",
    0x6B: "<BOLD_L>",
    0x6C: "<BOLD_M>",
    0x6D: "<COLON>",
    0x6E: "<LV>",
    0x6F: "ぅ",
    0x70: "<DO>",
    0x71: "◀",
    0x72: "<『>",
    0x73: "<ID>",
    0x74: "№",
    0x75: "<…>",
    0x76: "ぁ",
    0x77: "ぇ",
    0x78: "ぉ",
    0x79: "┌",
    0x7A: "─",
    0x7B: "┐",
    0x7C: "│",
    0x7D: "└",
    0x7E: "┘",
    0x7F: " ",
    0x80: "A",
    0x81: "B",
    0x82: "C",
    0x83: "D",
    0x84: "E",
    0x85: "F",
    0x86: "G",
    0x87: "H",
    0x88: "I",
    0x89: "J",
    0x8A: "K",
    0x8B: "L",
    0x8C: "M",
    0x8D: "N",
    0x8E: "O",
    0x8F: "P",
    0x90: "Q",
    0x91: "R",
    0x92: "S",
    0x93: "T",
    0x94: "U",
    0x95: "V",
    0x96: "W",
    0x97: "X",
    0x98: "Y",
    0x99: "Z",
    0x9A: "<(>",
    0x9B: "<)>",
    0x9C: ":",
    0x9D: ";",
    0x9E: "[",
    0x9F: "]",
    0xA0: "a",
    0xA1: "b",
    0xA2: "c",
    0xA3: "d",
    0xA4: "e",
    0xA5: "f",
    0xA6: "g",
    0xA7: "h",
    0xA8: "i",
    0xA9: "j",
    0xAA: "k",
    0xAB: "l",
    0xAC: "m",
    0xAD: "n",
    0xAE: "o",
    0xAF: "p",
    0xB0: "q",
    0xB1: "r",
    0xB2: "s",
    0xB3: "t",
    0xB4: "u",
    0xB5: "v",
    0xB6: "w",
    0xB7: "x",
    0xB8: "y",
    0xB9: "z",
    0xBA: "こ",
    0xBB: "さ",
    0xBC: "し",
    0xBD: "す",
    0xBE: "せ",
    0xBF: "そ",
    0xC0: "Ä",
    0xC1: "Ö",
    0xC2: "Ü",
    0xC3: "ä",
    0xC4: "ö",
    0xC5: "ü",
    0xC6: "ㅜ",
    0xC7: "ㅠ",
    0xC8: "ㅡ",
    0xC9: "ㅣ",
    0xCA: "ㅐ",
    0xCB: "ㅒ",
    0xCC: "ㅔ",
    0xCD: "ㅖ",
    0xCE: "ㅘ",
    0xCF: "ㅙ",
    0xD0: "'d",
    0xD1: "'l",
    0xD2: "'m",
    0xD3: "'r",
    0xD4: "'s",
    0xD5: "'t",
    0xD6: "'v",
    0xD7: "ら",
    0xD8: "リ",
    0xD9: "る",
    0xDA: "れ",
    0xDB: "ろ",
    0xDC: "わ",
    0xDD: "を",
    0xDE: "ん",
    0xDF: "っ",
    0xE0: "'",
    0xE1: "<PK>",
    0xE2: "<MN>",
    0xE3: "<->",
    0xE4: "゜",
    0xE5: "゛",
    0xE6: "<?>",
    0xE7: "<!>",
    0xE8: ".",
    0xE9: "&",
    0xEA: "é",
    0xEB: "ェ",
    0xEC: "▷",
    0xED: "▶",
    0xEE: "▼",
    0xEF: "♂",
    0xF0: "₩",
    0xF1: "×",
    0xF2: "<DOT>",
    0xF3: "/",
    0xF4: "<,>",
    0xF5: "♀",
    0xF6: "0",
    0xF7: "1",
    0xF8: "2",
    0xF9: "3",
    0xFA: "4",
    0xFB: "5",
    0xFC: "6",
    0xFD: "7",
    0xFE: "8",
    0xFF: "9",
}


@dataclass(frozen=True)
class CodeMaps:
    decode_two: dict[tuple[int, int], str]
    encode_two: dict[str, bytes]
    decode_one: dict[int, str]
    encode_one: dict[str, bytes]


def sha(data: bytes, algorithm: str = "sha256") -> str:
    return hashlib.new(algorithm, data).hexdigest()


def build_maps(rom: bytes) -> CodeMaps:
    start = FONT_FIRST_BANK * BANK_SIZE
    end = (FONT_LAST_BANK + 1) * BANK_SIZE
    font = rom[start:end]
    occupied: list[tuple[int, int]] = []
    for high in range(1, 0x0B):
        for low in range(0x100):
            tile_index = high * 0x100 + low
            tile = font[tile_index * 16 : (tile_index + 1) * 16]
            if any(tile):
                occupied.append((high, low))
    if len(occupied) != len(HANGUL_SEQUENCE) or len(occupied) != 2353:
        raise ValueError(
            f"Unexpected Hangul slot count: {len(occupied)} vs {len(HANGUL_SEQUENCE)}"
        )
    decode_two = dict(zip(occupied, HANGUL_SEQUENCE))
    decode_two.update({(0x0B, low): value for low, value in TABLE_B_MAP.items()})
    if len(decode_two) != 2419:
        raise ValueError(f"Unexpected two-byte mapping count: {len(decode_two)}")
    encode_two = {value: bytes(code) for code, value in decode_two.items()}
    if len(encode_two) != len(decode_two):
        raise ValueError("Two-byte character map is not reversible")
    decode_one = dict(SINGLE_BYTE_MAP)
    encode_one: dict[str, bytes] = {}
    for code, value in decode_one.items():
        encode_one[value] = bytes([code])
    return CodeMaps(decode_two, encode_two, decode_one, encode_one)


def decode_text(raw: bytes, maps: CodeMaps) -> tuple[str, list[str]]:
    out: list[str] = []
    unknown: list[str] = []
    i = 0
    while i < len(raw):
        value = raw[i]
        if 0x01 <= value <= 0x0B and i + 1 < len(raw):
            code = (value, raw[i + 1])
            mapped = maps.decode_two.get(code)
            if mapped is None:
                token = f"<UNK:{value:02X}{raw[i + 1]:02X}>"
                unknown.append(token)
                out.append(token)
            else:
                out.append(mapped)
            i += 2
            continue
        mapped = maps.decode_one.get(value)
        if mapped is None:
            token = f"<UNK:{value:02X}>"
            unknown.append(token)
            out.append(token)
        else:
            out.append(mapped)
        i += 1
    return "".join(out), unknown


def _tokenize(text: str, known_tokens: set[str]) -> list[str]:
    ordered = sorted((x for x in known_tokens if len(x) > 1), key=len, reverse=True)
    result: list[str] = []
    i = 0
    while i < len(text):
        match = next((token for token in ordered if text.startswith(token, i)), None)
        if match is None:
            result.append(text[i])
            i += 1
        else:
            result.append(match)
            i += len(match)
    return result


def encode_text(text: str, maps: CodeMaps) -> bytes:
    known = set(maps.encode_two) | set(maps.encode_one)
    encoded = bytearray()
    for token in _tokenize(text, known):
        if token in maps.encode_two:
            encoded.extend(maps.encode_two[token])
        elif token in maps.encode_one:
            encoded.extend(maps.encode_one[token])
        else:
            raise ValueError(f"Unencodable token: {token!r}")
    return bytes(encoded)


def split_terminated(region: bytes, expected: int) -> list[tuple[int, bytes]]:
    records: list[tuple[int, bytes]] = []
    cursor = 0
    for _ in range(expected):
        end = region.find(bytes([TERMINATOR]), cursor)
        if end < 0:
            raise ValueError("Missing Bank 6C terminator")
        records.append((cursor, region[cursor:end]))
        cursor = end + 1
    if cursor != len(region):
        raise ValueError(f"Unexpected trailing data: {len(region) - cursor} bytes")
    return records


def extract_bank_6c(rom: bytes, maps: CodeMaps) -> tuple[list[dict], bytes]:
    bank = rom[BANK_6C * BANK_SIZE : (BANK_6C + 1) * BANK_SIZE]
    move_tail = bank[0x164A:]
    move_end = max(i for i, value in enumerate(move_tail) if value) + 0x164A + 1
    definitions = [
        ("ITEM_NAMES", 0x0000, 0x09A1, "terminated", 256),
        ("TRAINER_CLASS_NAMES", 0x09A1, 0x0C4A, "terminated", 67),
        ("POKEMON_NAME_SLOTS", 0x0C4A, 0x164A, "fixed10", 256),
        ("MOVE_NAMES", 0x164A, move_end, "terminated", 251),
    ]
    rows: list[dict] = []
    rebuilt = bytearray(bank)
    all_unknown: list[str] = []
    for category, start, end, storage, count in definitions:
        region = bank[start:end]
        if storage == "terminated":
            records = split_terminated(region, count)
            rebuilt_region = bytearray()
            for index, (relative, raw) in enumerate(records):
                decoded, unknown = decode_text(raw, maps)
                all_unknown.extend(unknown)
                reencoded = encode_text(decoded, maps)
                if reencoded != raw:
                    raise AssertionError(f"Round-trip mismatch: {category} {index}")
                rebuilt_region.extend(reencoded)
                rebuilt_region.append(TERMINATOR)
                rows.append(
                    make_row(category, index, start + relative, raw, decoded, unknown, "VARIABLE")
                )
            if bytes(rebuilt_region) != region:
                raise AssertionError(f"Region mismatch: {category}")
            rebuilt[start:end] = rebuilt_region
        else:
            if len(region) != count * 10:
                raise ValueError("Fixed name table boundary mismatch")
            for index in range(count):
                record = region[index * 10 : (index + 1) * 10]
                # Five two-byte Hangul glyphs can occupy all ten bytes.  Such
                # names legitimately have no terminator inside the fixed slot.
                term = record.find(bytes([TERMINATOR]))
                if term < 0:
                    raw = record
                    suffix = b""
                else:
                    raw = record[:term]
                    suffix = record[term:]
                decoded, unknown = decode_text(raw, maps)
                all_unknown.extend(unknown)
                reencoded = encode_text(decoded, maps) + suffix
                if reencoded != record:
                    raise AssertionError(f"Round-trip mismatch: {category} {index}")
                rows.append(
                    make_row(
                        category,
                        index,
                        start + index * 10,
                        raw,
                        decoded,
                        unknown,
                        "FIXED_10",
                        suffix,
                    )
                )
    if all_unknown:
        raise ValueError(f"Undefined codes found: {sorted(set(all_unknown))}")
    return rows, bytes(rebuilt)


def make_row(
    category: str,
    index: int,
    bank_offset: int,
    raw: bytes,
    text: str,
    unknown: list[str],
    storage: str,
    suffix: bytes = b"",
) -> dict:
    cpu_address = 0x4000 + bank_offset
    return {
        "category": category,
        "index_zero_based": index,
        "index_one_based": index + 1,
        "bank_hex": "0x6C",
        "bank_offset_hex": f"0x{bank_offset:04X}",
        "cpu_address_hex": f"0x{cpu_address:04X}",
        "file_offset_hex": f"0x{BANK_6C * BANK_SIZE + bank_offset:06X}",
        "storage": storage,
        "raw_length": len(raw),
        "raw_hex": raw.hex(" "),
        "fixed_suffix_hex": suffix.hex(" "),
        "decoded_text": text,
        "undefined_code_count": len(unknown),
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("gold_rom", type=Path)
    parser.add_argument("silver_rom", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    gold = args.gold_rom.read_bytes()
    silver = args.silver_rom.read_bytes()
    maps_gold = build_maps(gold)
    maps_silver = build_maps(silver)
    if maps_gold.decode_two != maps_silver.decode_two:
        raise ValueError("Gold/Silver two-byte maps differ")
    rows_gold, bank_gold = extract_bank_6c(gold, maps_gold)
    rows_silver, bank_silver = extract_bank_6c(silver, maps_silver)
    original_gold = gold[BANK_6C * BANK_SIZE : (BANK_6C + 1) * BANK_SIZE]
    original_silver = silver[BANK_6C * BANK_SIZE : (BANK_6C + 1) * BANK_SIZE]
    if bank_gold != original_gold or bank_silver != original_silver:
        raise AssertionError("Bank 6C lossless rebuild failed")
    if rows_gold != rows_silver or original_gold != original_silver:
        raise AssertionError("Gold/Silver Bank 6C content differs")
    bank_start = BANK_6C * BANK_SIZE
    bank_end = (BANK_6C + 1) * BANK_SIZE
    rebuilt_gold_rom = gold[:bank_start] + bank_gold + gold[bank_end:]
    rebuilt_silver_rom = silver[:bank_start] + bank_silver + silver[bank_end:]
    if rebuilt_gold_rom != gold or rebuilt_silver_rom != silver:
        raise AssertionError("Full-ROM lossless reconstruction failed")

    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "bank_6c_names_utf8.csv", rows_gold)
    (args.output / "bank_6c_names_utf8.json").write_text(
        json.dumps(rows_gold, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    charmap_rows = [
        {
            "code_hex": f"0x{high:02X}{low:02X}",
            "width_bytes": 2,
            "text": value,
            "kind": "HANGUL" if high <= 0x0A else "TABLE_B_SYMBOL",
        }
        for (high, low), value in sorted(maps_gold.decode_two.items())
    ]
    charmap_rows += [
        {
            "code_hex": f"0x{code:02X}",
            "width_bytes": 1,
            "text": value,
            "kind": "LITERAL" if len(value) == 1 and value != "@" else "CONTROL_OR_TOKEN",
        }
        for code, value in sorted(maps_gold.decode_one.items())
    ]
    write_csv(args.output / "korean_charmap.csv", charmap_rows)
    (args.output / "korean_charmap.json").write_text(
        json.dumps(charmap_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    comparison_rows = [
        {
            "category": row["category"],
            "index_zero_based": row["index_zero_based"],
            "index_one_based": row["index_one_based"],
            "original_gs_korean": row["decoded_text"],
            "latest_official_korean": "",
            "final_korean": "",
            "official_source": "",
            "verification_status": "PENDING_OFFICIAL_CROSSCHECK",
            "change_reason": "",
            "bank_hex": row["bank_hex"],
            "cpu_address_hex": row["cpu_address_hex"],
        }
        for row in rows_gold
    ]
    write_csv(args.output / "official_name_comparison_master.csv", comparison_rows)
    (args.output / "official_name_comparison_master.json").write_text(
        json.dumps(comparison_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    summary = {
        "gold_sha1": sha(gold, "sha1"),
        "silver_sha1": sha(silver, "sha1"),
        "bank_6c_sha256": sha(original_gold),
        "two_byte_mappings": len(maps_gold.decode_two),
        "hangul_mappings": len(HANGUL_SEQUENCE),
        "table_b_mappings": len(TABLE_B_MAP),
        "single_byte_values": len(maps_gold.decode_one),
        "single_byte_literals": sum(
            len(value) == 1 and value != "@" for value in maps_gold.decode_one.values()
        ),
        "records": len(rows_gold),
        "records_by_category": {
            category: sum(row["category"] == category for row in rows_gold)
            for category in (
                "ITEM_NAMES",
                "TRAINER_CLASS_NAMES",
                "POKEMON_NAME_SLOTS",
                "MOVE_NAMES",
            )
        },
        "undefined_codes": sum(row["undefined_code_count"] for row in rows_gold),
        "gold_bank_6c_roundtrip_sha256": sha(bank_gold),
        "silver_bank_6c_roundtrip_sha256": sha(bank_silver),
        "gold_bank_6c_lossless": bank_gold == original_gold,
        "silver_bank_6c_lossless": bank_silver == original_silver,
        "gold_full_rom_roundtrip_sha1": sha(rebuilt_gold_rom, "sha1"),
        "silver_full_rom_roundtrip_sha1": sha(rebuilt_silver_rom, "sha1"),
        "gold_full_rom_lossless": rebuilt_gold_rom == gold,
        "silver_full_rom_lossless": rebuilt_silver_rom == silver,
        "gold_silver_bank_6c_identical": original_gold == original_silver,
        "crosscheck": "Narishma-gb/pokegold-kr constants/charmap",
    }
    (args.output / "phase2_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
