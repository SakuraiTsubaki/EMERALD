# External-event permanent-access scope

## Definition

이 프로젝트에서 "외부 이벤트 상시화"는 외부 장치나 과거 배포를 재현해야만 콘텐츠가 생기는 상태를 제거하는 것을 뜻합니다.

단순히 모든 완료 플래그를 켜는 것이 아닙니다. 그렇게 하면 이벤트를 이미 끝낸 것으로 처리해 전투/보상 자체가 사라질 수 있으므로, 원본 이벤트 진행과 완료 상태는 가능한 한 그대로 유지합니다.

## Ticket events: distribute the ticket, keep the original event

티켓 계열은 목적지 자체를 강제로 항상 표시하지 않습니다.

플레이어가 상시 배달원에게서 다음 이벤트 아이템을 받을 수 있게 하고, 이후 항구와 섬 이벤트는 원본 Emerald 로직을 그대로 사용합니다.

- Eon Ticket
- Aurora Ticket
- Mystic Ticket
- Old Sea Map

원본 `src/script_menu.c`의 S.S. Tidal 목적지 판정은 **티켓 아이템과 해당 ship-enable flag를 모두 확인**합니다. 원본 Mystery Gift/Record Mixing 지급 루틴 역시 티켓을 줄 때 그 플래그를 함께 설정합니다.

따라서 EMERALD 패치도 목적지 코드는 건드리지 않고, 티켓 수령 시에만 원본과 동일한 ship-enable flag를 설정합니다. 플레이어에게 보이는 변경점은 "외부 배포 없이 티켓을 받을 수 있다"는 것뿐입니다.

포획/격파/완료 플래그는 미리 설정하지 않습니다.

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

티켓 이외의 항목은 Wonder Card RAM script, e-Reader trainer 구조체 등 외부에서 실제 payload가 들어오는 타입이 있으므로 각각 원본 데이터를 ROM 내부 데이터로 승격하는 방식으로 처리합니다.

## e-Reader data-driven scope

다음은 별도 데이터 내장 작업이 필요합니다.

- Sootopolis Mystery Events House visiting trainer
- e-Reader trainer payload
- Trainer Hill e-Reader trainer/map data
- Wonder Card / Wonder News saved data and RAM scripts

`manifests/external-events.yml`에서 구현 완료 전까지 계속 추적합니다.
