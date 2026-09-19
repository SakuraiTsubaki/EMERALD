# External payload research

## Pokémon Battle e Emerald

일본 전용 `Pokémon Battle e Emerald`는 Trainer Hill을 e-Reader 데이터로 변경하는 기능이다.

- 본 세트: 64장의 Trainer 카드
- 프로모션: 2장의 Emerald Trainer 카드
- 따라서 게임 payload 대상으로 추적할 Trainer 카드는 총 66장
- 별도의 19장 map puzzle sub-set은 dot-code가 없는 수집용 카드이므로 ROM에 주입할 e-Reader payload 대상으로 세지 않는다.
- Trainer 카드는 트레이너 데이터뿐 아니라 스캔 순서에 따라 사용하는 파티와 해당 층의 레이아웃에도 영향을 준다.
- 최대 8장의 Trainer 카드를 한 Trainer Hill 구성에 스캔한다.

원본 카드 이미지 자체가 아니라, 보존된 raw e-Reader dump를 식별하고 검증하기 위해 카드 ID와 SHA-1을 별도 manifest로 관리한다.

Sources:
- https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_Battle_e_Emerald
- https://gist.github.com/Bl4ckSh4rk/32695e2e5b27ecb8e946e20ac0d79c99

## Sootopolis Mystery Events House

Emerald에는 Sootopolis의 Mystery Events House와 `BattleTowerEReaderTrainer` 저장 구조가 남아 있다. 외부 e-Reader Trainer payload가 유효할 때 뒤쪽 방을 열고 해당 트레이너와 반복 배틀할 수 있는 경로다.

이 기능은 단순 플래그 해제로 끝나지 않는다. `BattleTowerEReaderTrainer` 구조체의 실제 trainer payload와 checksum이 필요하므로, 영구 상시화에서는 원본/보존 카드 데이터를 ROM 내부 테이블로 옮기고 선택한 데이터를 save 구조체에 복사하는 방식으로 구현한다.

## Enigma Berry distinction

e-Card Berry payload는 Ruby/Sapphire의 e-Reader Berry 기능으로 보존 자료가 확인된다. Berry 자체 데이터는 Gen III ROM에 고정 데이터로 존재하는 것이 아니라 save에 external payload로 들어가며, 게임은 Enigma Berry 슬롯을 사용한다.

Emerald 소스에도 `SetEnigmaBerry`와 Mystery Event 명령이 남아 있지만, 이것을 `Pokémon Battle e Emerald` 정식 카드 이벤트와 동일하게 취급하면 범위가 섞인다.

따라서 EMERALD에서는 다음과 같이 분류한다.

1. **Emerald 실제 외부 이벤트/카드 콘텐츠**: 반드시 상시화.
2. **Emerald 엔진에 남아 있는 범용 e-Reader/Mystery Event 기능**: 호환성 보존 대상으로 별도 추적.
3. Ruby/Sapphire 전용 카드 데이터 자체는 Emerald 정식 이벤트로 잘못 포함하지 않는다.

Reference:
- https://projectpokemon.org/home/files/file/3505-e-card-berries/
