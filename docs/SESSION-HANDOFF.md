# 세션 인계 메모

새 Claude 세션이 이 저장소에서 이어 작업할 때 **가장 먼저 읽는 문서**다. 이전 세션의 대화는 새 세션에 보이지 않으므로, 필요한 맥락은 모두 여기와 아래 링크한 파일에 있다.

- 작성: 2026-11-15
- 작업 브랜치: `claude/wizardly-ride-2cquo9` (이전 브랜치 `claude/kind-edison-s3bfex`를 병합해 이어감. 기본 브랜치에는 아직 합쳐지지 않음)

## 1. 먼저 읽을 파일 (이 순서로)

1. `CLAUDE.md`: 이 저장소의 목적, 작업 방식, 회사 데이터 규칙, 폴더 구조, 브리핑 형식
2. `docs/game-context.md`: 카오스 제로 나이트메어(카제나) 맥락. 특히 「사용자가 알려준 사실」 표
3. `plans/story-map-pin-move/decisions.md`, `plans/map-move-tool/decisions.md`: 확정된 결정과 변경 이력
4. 필요할 때 `plans/*/spec.md` (기획서 원본)
5. 스킬: `.claude/skills/plan-interview`, `plan-doc`, `plan-handoff`

## 2. 사용자에 대해 알아둘 것

- 게임 회사 기획자. 콘텐츠·이벤트, 연출 시스템·연출 기능을 기획한다.
- **주로 폰으로 이동 중에 작업한다.** 긴 설명보다 짧은 브리핑, 타이핑보다 탭으로 고르는 질문(AskUserQuestion)을 선호한다. 결정할 것이 여러 개면 객관식 질문으로 묶어서 묻는다.
- 인터뷰로 방향을 잡으면 Claude가 끝까지 만들고 → 브리핑 → 사용자가 폴리싱 피드백 → 반영하는 흐름을 원한다.
- **못생긴 문서를 매우 싫어한다.** 결과물은 `plan-doc` 스킬과 샘플 디자인을 따른다.
- 문서 문체는 한국어 간결체("~한다").
- 이 저장소는 회사 밖 초안 공간이다. 회사 데이터는 없고, 완성되면 인계 파일을 로컬로 저장해 회사 PC의 회사 Claude에게 넘긴다(한 방향).
- 확인된 회사 정보: 시간은 ms, 글자는 문자열 테이블 키, Actor 테이블(이름·리소스 경로), 스토리에 자동 진행·배속(켬/끔)·다시보기·대사 로그 있음, 가로 화면. 상세는 `docs/game-context.md`.
- 사용자가 결정하지 않은 값은 `검증필요`, 미룬 것은 `미정`, 사용자가 정한 것만 `확정`이다. 이 규칙을 엄격히 지킨다.

## 3. 진행 중인 기획

| 기획 | 폴더 | 버전 | 상태 |
|---|---|---|---|
| 스토리 맵 핀 이동 연출 | `plans/story-map-pin-move/` | v0.27 | **회사에 내는 본 문서는 핵심 기획서 `core.md`**(2~3쪽, 규칙 12개). `spec.md`는 참고 자료, 구현·아트·사운드 전달사항은 `delivery.md`. 5차 단순화(작성 기준·검수·작업 목록·용어 부록 삭제, 부록은 A~G). 배경 2048×1152 고정. 구현 규칙은 부록 G |
| 맵 이동 연출 편집 툴 | `plans/map-move-tool/` | v0.27 | 검사는 오류만(경고 없음). 단축키는 부록 C, 편집 조작 세부는 부록 D, 검증·미결은 부록 E. 사용 안내 문서는 없앴다 |

### 기획 요약 (스토리 맵 핀 이동 연출)
스토리 중 배경 지도 위에서 핀(Actor)이 경로를 따라 이동하며 위치 정보를 보여주는 연출. 장소 마크, 이어가기(앞 연출 끝 상태에서 시작), 스토리 행의 열 2개(`link_map_scene_id`, `map_close`)로 맵 열기·닫기, 속도 프리셋, 출발 조건, 자동 곡선 + 베지어 핸들.

데이터는 **엑셀 `map_scene` 1개 + 장소 JSON(파일 이름이 id, 같은 배경에 여러 개 가능) + 연출마다 연출 JSON 1개**(핀, 경로 점, 장소 보임). 배경은 기존 `story_resource_list` id를 장소 JSON이 가리킨다. JSON에는 version을 두지 않는다(회사는 SVN·Git으로 이력 관리). 장소 이름은 선택(이름 없으면 게임에 안 보이는 기준점). 회사 규칙: 행마다 `id`, 참조는 `link_*_id`, 소문자 + 밑줄, 그룹 없음. 이름은 전부 자리표시이고 기획서 「회사 데이터 연결」에 회사에서 확인할 질문과 이름 대응표가 있다.

### 2026-11-15 세션에서 한 일
- 두 기획서를 회사 전달 수준으로 보완(상태 전이표, 계산 규칙, 구현 전달사항, 검수 항목, 작업 목록, 회사 데이터 연결)
- 프로토타입을 탭 3개(스토리 시연 / 편집 툴 / 데이터)로 재작성. 내보내는 JSON이 기획서 예시와 글자 단위로 같다
- `HANDOFF.md` 작성(두 기획서 전문 포함)

### 최근 사용자 피드백 흐름 (툴 UX)
- 편집 모드에서 누르다 점이 찍히는 실수 → **점·장소 생성은 더블클릭만**, 한 번 누르기는 선택(E-01 확정)
- 장소를 누르면 장소 편집으로, 핀·점을 누르면 핀·경로 편집으로 자동 전환(E-10 확정)
- 장소 속성 패널에 X, Y 입력칸(M-06 확정). 방향키 미세 이동과 점 좌표 입력칸은 넣지 않기로 함

### 남은 것
- 사용자 확인: 남은 제안 R-48, R-51(회사 검토에 맡겨도 된다). 2026-11 검토 결정 4건과 복잡도 줄이기(이어가기 자동 출발, 출발 조건 2종, 문서 표기 정리)는 반영 완료
- 문서 규칙: 설정 테이블은 없다. 수치는 규칙에 숫자로 쓰고, UI 크기와 툴 내부 값은 쓰지 않는다(UI 팀·툴 몫). 자리표시 이유뿐인 표에는 배지를 붙이지 않는다. HTML에서 확정 배지는 그리지 않는다(배지 없음 = 확정)
- 단순화 원칙(2026-11-22): 연출 작성 기준, 품질 경고, 검수·작업 목록처럼 사람이나 다른 팀이 정할 것은 기획서에 쓰지 않는다. "나중에 정한다"는 말도 남기지 않는다.
- 문서 묶음 버전은 하나다(연출·툴·핵심·전달사항·프로토 공통, 지금 v0.27). 함께 올린다. 규칙을 바꾸면 `core.md`의 해당 줄도 같이 고친다. 변경 이력은 문서에 최근 3개만, 나머지는 `decisions.md`
- 복잡성 검토 기준(K1~K6 기획 요소, D1~D6 문서 읽기)은 `review-2026-11.md` 「2차 복잡성 검토」에 있다. 새 기능을 넣을 때 이 기준으로 먼저 본다
- 회사 확인: 기획서 「부록 F 회사 데이터 연결」 표와 「검증·미결 목록」
- 프로그램실 회의 안건: 툴 플랫폼, 엑셀 행 반영 방식, 편의 기능 범위, 자유 그리기
- 사용자 결정이 바뀌면 `spec.md`를 고친 뒤 `python3 plans/story-map-pin-move/src/gen_handoff.py`로 `HANDOFF.md`를 다시 만든다(HANDOFF는 직접 고치지 않는다)

## 4. 작업 도구와 절차

```bash
pip install markdown                                   # 처음 한 번
python3 tools/build_spec.py plans/<슬러그>             # spec.md → spec.html
python3 plans/story-map-pin-move/src/gen_visuals.py     # 시안·요약 다시 생성
python3 plans/story-map-pin-move/src/gen_handoff.py     # HANDOFF.md 다시 생성
python3 tools/build_spec.py plans/story-map-pin-move --md delivery.md   # 구현·아트·사운드 전달사항 HTML
```

- **원본은 항상 `spec.md`**. HTML은 직접 고치지 않는다. 시안·요약은 `src/gen_visuals.py`를 고친다.
- 프로토타입: `plans/story-map-pin-move/proto/index.html` (단일 HTML, 직접 수정, 탭 3개). 고친 뒤에는 Playwright로 오류·폰 폭(400px)·실제 조작을 확인한다. 페이지의 `window.__proto`(state, schedule, jsonText, info 등)로 상태를 읽어 검증할 수 있다. 기획서의 예시 JSON과 프로토의 「데이터」 탭 출력이 같아야 한다.
- 게시: Artifact로 게시해 사용자가 폰에서 본다. 게시용 조각은 `--artifact <경로>` 옵션이나 `python3 tools/artifact_fragment.py 입력.html 출력.html`로 만든다.
- 기존 게시물(2026-11-16 기준 최신. 같은 주소로 갱신하려면 Artifact 도구에 아래 URL을 넘기고, 먼저 `path` 없이 read로 전체를 읽어야 한다. 파일이 커서 부담되면 새 주소로 게시하고 여기 링크를 바꾼다):
  - 검토 리포트(2026-11): https://claude.ai/artifact/WtMC1Fm3qS939KdpAQ7r4E
  - 회의용 한 장(리드·PD): https://claude.ai/artifact/ATo7ETCCrbn7aebjtBF69D
  - 기획서: https://claude.ai/artifact/Pyeta9tKgdRzDXNPwvG8Lq
  - 화면 시안: https://claude.ai/artifact/JYmuQfx4EmzcSKiCpXDR8f
  - 동작 프로토타입: https://claude.ai/artifact/PG9AVSaonaYP694yNCsEzZ
  - 편집 툴 기획서: https://claude.ai/artifact/JGXZ6HSCYqP6DmyiQdHx3b
  - (보관) 툴 사용 안내, v0.22에서 문서 삭제: https://claude.ai/artifact/Hyte4xzjAhnT5UwPi3Gw7H
- 작업 단위마다 커밋·푸시. 커밋 메시지는 `<슬러그> v0.x: 내용`. PR은 사용자가 요청할 때만.
