# EMERALD

Pokémon Emerald의 외부 배포/외부 장치 의존 이벤트를 게임 내부에서 상시 이용 가능하게 만드는 작업 저장소입니다.

## 목표

외부 배포, Wonder Card, Mystery Gift / Mystery Event, Record Mixing, e-Reader 등 외부 입력이 없으면 접근할 수 없던 콘텐츠를 ROM 자체에서 접근 가능하게 만듭니다.

"상시화"의 원칙은 다음과 같습니다.

- 외부 배포 서버, 무선 어댑터, e-Reader, 다른 카트리지에 의존하지 않습니다.
- 원래 한 번만 잡거나 한 번만 받는 콘텐츠의 완료 플래그는 보존합니다.
- **티켓 이벤트는 목적지를 강제 해제하지 않고 티켓을 상시 지급합니다. 이후 이벤트는 원본 흐름을 그대로 사용합니다.**
- 단순히 세이브 플래그를 미리 켜는 방식에만 의존하지 않습니다. 기존 세이브에서도 ROM 수정만으로 접근 가능해야 합니다.
- 언어 기준은 일본판을 최우선으로 하고, 한국어 자료가 없으면 영어를 기준으로 대조한 뒤 독일어/프랑스어/이탈리아어/스페인어판에 확장합니다.
- ROM 바이너리는 GitHub에 올리지 않습니다. 패치, 분석, 매니페스트, 검증 자료만 관리합니다.

## 현재 작업

### Ticket events

미로마을(Littleroot Town)에 새 상시 NPC를 추가하고, Eon Ticket / Aurora Ticket / Mystic Ticket / Old Sea Map 중 하나를 선택해 한 번에 하나씩 받을 수 있게 합니다. 항구/목적지/전설 이벤트는 원본 Emerald 로직을 그대로 둡니다.

- Southern Island / Eon Ticket
- Birth Island / Aurora Ticket
- Navel Rock / Mystic Ticket
- Faraway Island / Old Sea Map

패치: `patches/pokeemerald/0002-littleroot-event-ticket-npc.patch`

### Item table normalization

Emerald의 아이템 ID와 게임 파라미터를 최종 기준으로 두고, DP / Pt / HGSS 아이템 테이블은 비교·확장 소스로 사용합니다.

- Emerald 원본 377개 슬롯 파라미터: `manifests/emerald-item-parameters.csv`
- Emerald ↔ Gen IV 공식 AGB 대응: `manifests/emerald-gen4-item-crosswalk.csv`
- DP / Pt / HGSS ID 비교: `manifests/gen4-item-id-crosswalk.csv`
- 분석 문서: `research/emerald-gen4-item-crosswalk.md`, `research/gen4-item-table.md`

기존 Emerald 아이템은 번호와 동작을 유지하고, 이후 세대 전용 아이템은 Emerald 쪽 확장 ID를 별도로 배정하는 방식으로 진행합니다.


### Arceus all-generation form mechanics

Branch: `feature/arceus-all-gen`

Arceus is represented as one persistent species with explicit form metadata and battle-derived form state.

- Gen IV/V: sixteen Plates / 17 playable forms with generation-specific item-manipulation and Transform rules.
- Gen VI: Pixie Plate / Fairy support for 18 playable type forms.
- Gen VII: type Z-Crystals also drive Multitype forms while Judgment remains Plate-only.
- BDSP / Gen IX: held-Plate model, with a documented Gen IX Terastallization guard.
- Pokémon Legends: Arceus: active-use Plates, Blank Plate, and Legend Plate target-derived Judgment transformation.
- Persistent PLA form state uses the existing 16-bit Pokémon substruct filler slot without enlarging the save structure.
- Judgment uses a separate move-category resolver so it remains Special under Emerald's type-based physical/special engine.
- Item extension IDs 377-413: `manifests/arceus-item-extensions.csv`
- Fairy chart additions: `manifests/fairy-type-chart-extension.csv`
- Core mechanics: `src/extensions/arceus/`
- Integration: `patches/arceus/INTEGRATION.md`
- Acceptance tests: `tests/arceus_behavior.md`

### Other external events

- Altering Cave Mystery Gift encounter sets
- Mystery Gift / Mystery Event 기능
- Wonder Card + saved RAM script
- Surf Pichu gift script
- Battle Count Card / Stamp Card
- Sootopolis visiting e-Reader trainer
- e-Reader trainer data
- Trainer Hill e-Reader trainer/map data

전체 범위와 구현 상태는 `manifests/external-events.yml`을 기준으로 추적합니다.

## Reference

코어 소스 대조 기준은 `pret/pokeemerald`의 공개 decompilation입니다. 실제 ROM 패치는 각 지역/언어 ROM을 별도로 서명 검증한 뒤 생성합니다.
