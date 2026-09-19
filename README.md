# EMERALD

Pokémon Emerald의 외부 배포/외부 장치 의존 이벤트를 게임 내부에서 상시 이용 가능하게 만드는 작업 저장소입니다.

## 목표

외부 배포, Wonder Card, Mystery Gift / Mystery Event, Record Mixing, e-Reader 등 외부 입력이 없으면 접근할 수 없던 콘텐츠를 ROM 자체에서 접근 가능하게 만듭니다.

"상시화"의 원칙은 다음과 같습니다.

- 외부 배포 서버, 무선 어댑터, e-Reader, 다른 카트리지에 의존하지 않습니다.
- 원래 한 번만 잡거나 한 번만 받는 콘텐츠의 완료 플래그는 보존합니다.
- 단순히 세이브 플래그를 미리 켜는 방식에만 의존하지 않습니다. 기존 세이브에서도 ROM 수정만으로 접근 가능해야 합니다.
- 언어 기준은 일본판을 최우선으로 하고, 한국어 자료가 없으면 영어를 기준으로 대조한 뒤 독일어/프랑스어/이탈리아어/스페인어판에 확장합니다.
- ROM 바이너리는 GitHub에 올리지 않습니다. 패치, 분석, 매니페스트, 검증 자료만 관리합니다.

## 현재 작업

### Core external events

- Southern Island / Eon Ticket
- Birth Island / Aurora Ticket
- Navel Rock / Mystic Ticket
- Faraway Island / Old Sea Map
- Altering Cave Mystery Gift encounter sets

첫 소스 패치는 `patches/pokeemerald/0001-always-available-core-external-events.patch`에 있습니다.

### Data-driven external events

다음 항목도 전체 상시화 범위에 포함합니다.

- Mystery Gift / Mystery Event 기능
- Wonder Card + saved RAM script
- Surf Pichu gift script
- Battle Count Card / Stamp Card
- Sootopolis visiting e-Reader trainer
- e-Reader trainer data
- Trainer Hill e-Reader trainer/map data
- Enigma Berry external event data

전체 범위와 구현 상태는 `manifests/external-events.yml`을 기준으로 추적합니다.

## Reference

코어 소스 대조 기준은 `pret/pokeemerald`의 공개 decompilation입니다. 실제 ROM 패치는 각 지역/언어 ROM을 별도로 서명 검증한 뒤 생성합니다.
