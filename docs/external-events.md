# External-event permanent-access scope

## Definition

이 프로젝트에서 "외부 이벤트 상시화"는 외부 장치나 과거 배포를 재현해야만 콘텐츠가 생기는 상태를 제거하는 것을 뜻합니다.

단순히 모든 완료 플래그를 켜는 것이 아닙니다. 그렇게 하면 이벤트를 이미 끝낸 것으로 처리해 전투/보상 자체가 사라질 수 있으므로, **접근 게이트만 제거하고 완료 상태는 원래 로직을 유지**하는 것을 기본 원칙으로 합니다.

## Built-in event islands

`pret/pokeemerald`의 `src/script_menu.c`에서 S.S. Tidal 목적지는 다음 두 조건을 동시에 요구합니다.

- Eon Ticket + `FLAG_ENABLE_SHIP_SOUTHERN_ISLAND`
- Mystic Ticket + `FLAG_ENABLE_SHIP_NAVEL_ROCK`
- Aurora Ticket + `FLAG_ENABLE_SHIP_BIRTH_ISLAND`
- Old Sea Map + `FLAG_ENABLE_SHIP_FARAWAY_ISLAND`

Core patch 0001은 이 네 목적지를 티켓 및 배포 플래그와 무관하게 목적지 목록에 포함시킵니다. 포획/격파 완료 플래그는 수정하지 않습니다.

## Altering Cave

원본은 `VAR_ALTERING_CAVE_WILD_SET` 값으로 외부 Mystery Gift가 선택한 조우 테이블을 사용합니다.

Core patch 0001은 조우 헤더를 결정할 때 모든 Altering Cave 테이블 중 하나를 선택하도록 변경합니다. 따라서 더 이상 외부 Mystery Gift로 테이블을 바꿀 필요가 없고 모든 세트가 게임 내부에서 계속 등장 가능합니다.

## Mystery Gift / Mystery Event scripts already present in ROM source

공개 소스의 `data/mystery_gift.s`에는 다음 스크립트가 포함됩니다.

- Stamp Card
- Surf Pichu
- Visiting Trainer
- Battle Count Card
- Aurora Ticket
- Mystic Ticket
- Altering Cave
- Old Sea Map

Eon Ticket은 별도로 Record Mixing / Cable Club 경로에 있습니다.

이 항목들은 단순 게이트 제거만으로는 모두 재현되지 않습니다. Wonder Card RAM script, e-Reader trainer 구조체, Enigma Berry 데이터처럼 **외부에서 실제 payload가 들어오는 타입**이 있기 때문입니다. 따라서 다음 단계에서는 이 payload를 ROM 내부 데이터로 승격하고 게임 내 이벤트 허브에서 선택할 수 있게 합니다.

## e-Reader data-driven scope

다음은 반드시 별도 데이터 내장 작업이 필요합니다.

- Sootopolis Mystery Events House visiting trainer
- e-Reader trainer payload
- Trainer Hill e-Reader trainer/map data
- Enigma Berry payload
- Wonder Card / Wonder News saved data and RAM scripts

이 항목도 제외하지 않습니다. `manifests/external-events.yml`에서 구현 완료 전까지 계속 추적합니다.
