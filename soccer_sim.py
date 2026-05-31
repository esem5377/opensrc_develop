import random
import json
from openai import OpenAI


client = OpenAI(
    api_key="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"
)


class Player:
    def __init__(self, name, team, position, value):
        self.name = name
        self.team = team
        self.position = position
        self.value = value


players = [
    Player("조현우", "울산 현대", "GK", 10),
    Player("기성용", "포항 스틸러스", "MF", 13),
    Player("홍철", "강원 FC", "DF", 5),
    Player("주민규", "대전 하나", "FW", 9),
    Player("이승우", "전북 현대", "MF", 10),
    Player("린가드", "FC 서울", "MF", 10),
    Player("이동경", "김천 상무", "MF", 10),
    Player("김경민", "광주 FC", "GK", 9),
    Player("이용", "수원 FC", "DF", 12),
    Player("세징야", "대구 FC", "MF", 12),
]


budget = 50
current_month = 1
current_year = 2025
transfer_window_open = False


def show_all_players():
    global budget
    print(f"\n[선수 목록] (예산: {budget}억)\n")


    print("[내 팀 선수]")
    found_myteam = False
    for i, p in enumerate(players):
        if p.team == "MyTeam":
            found_myteam = True
            print(f"{i+1}. {p.name} | {p.team} | {p.position} | {p.value}억")
    if not found_myteam:
        print(">> 내 팀 없음")


    print("\n[다른 팀 선수]")
    found_other = False
    for i, p in enumerate(players):
        if p.team != "MyTeam":
            found_other = True
            print(f"{i+1}. {p.name} | {p.team} | {p.position} | {p.value}억")
    if not found_other:
        print(">> 다른 팀 없음")


def transfer_player():
    global budget, transfer_window_open


    if not transfer_window_open:
        print(">> 이적시장 닫힘 (1월/7월만 열림)\n")
        return


    name = input("영입할 선수 이름: ").strip()


    for p in players:
        if p.name == name and p.team != "MyTeam":
            if budget < p.value:
                print(f">> 예산 부족! 현재 {budget}억\n")
                return
            budget -= p.value
            p.team = "MyTeam"
            print(f">> 영입 성공! 남은 예산 {budget}억\n")
            return


    print(">> 선수 없음\n")


def fallback_random_update():
    for p in players:
        delta = random.randint(-3, 3)
        p.value = max(1, min(30, p.value + delta))
    print("[랜덤 업데이트 적용됨]\n")


def update_player_values_ai():
    
    info_lines = []
    for p in players:
        is_my = (p.team == "MyTeam")
        info_lines.append(f"- name: {p.name}, team: {p.team}, position: {p.position}, value: {p.value}, myteam: {is_my}")
    player_info_text = "\n".join(info_lines)


    
    user_prompt = f"""
다음은 선수들의 현재 정보와 2025 시즌 K리그 최신 순위 정보야.


[선수 정보]
{player_info_text}


[K리그 2025 시즌 순위]


1위 전북
2위 대전
3위 김천상무
4위 포항
5위 FC서울
6위 강원
7위 광주
8위 안양
9위 울산
10위 수원
11위 제주
12위 대구


아래 조건을 참고해서 각 선수의 가치 변동값을 -3 ~ +3 사이의 정수로 만들어줘.


[반영해야 하는 조건]
- 상위권 팀(1~2위)에 소속된 선수는 가치 유지 및 소폭 상승(~+2) 가능성이 매우 높다.
- 하위권 팀(9~12위)에 소속된 선수는 가치 하락 가능성이 높다.
- 중위권 팀(3위~8위)에 소속된 선수는 가치 변동 가능성이 적다. 그렇다고 아예 변하지 않는 것은 아니다.
- 이적 직후(MyTeam으로 변경된 선수)는 적응 단계인 변화 반영 → ±2 범위 내 변동
- 포지션별 경향:
  • FW: 득점 기여 가능성이 크므로 변동 폭이 크다(-3 ~ +2)
  • MF: 경기 영향력이 크므로 -2 ~ +2
  • DF/GK: 안정적 포지션 → -1 ~ +1
- 팀과의 궁합(MyTeam에 오래 있었거나 강팀으로 이적한 경우) → 상승 요인
- 기존 value가 높은 선수는 변동 폭 감소


출력은 반드시 아래 JSON 형식으로만 출력해야 한다:


{{"value_changes": [x1, x2, x3, ..., x{len(players)}]}}


여기서 x1은 첫 번째 선수, x2는 두 번째 선수 ... 순서대로 players 배열 순서를 따름.
다른 설명 없이 JSON만 출력해.
"""


    try:
        completion = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {"role": "system", "content": "너는 축구 시뮬레이터 AI 엔진이다. JSON만 출력해야 한다."},
                {"role": "user", "content": user_prompt},
            ]
        )


        content = completion.output[0].content[0].text.strip()
        data = json.loads(content)


        changes = data.get("value_changes", [])
        if len(changes) != len(players):
            print("AI 응답 오류 → 랜덤 적용")
            fallback_random_update()
            return


        for i, delta in enumerate(changes):
            d = int(delta)
            players[i].value = max(1, min(30, players[i].value + d))


        print("\n[AI 기반 선수 가치 업데이트 완료]\n")


    except Exception as e:
        print("AI 호출 에러:", e)
        fallback_random_update()



def advance_time():
    global current_month, current_year, transfer_window_open


    current_month += 2
    if current_month > 12:
        current_month = 1
        current_year += 1


    print(f"\n현재 날짜: {current_year}/{current_month:02d}")
    update_player_values_ai()


    if current_month in (1, 7):
        transfer_window_open = True
        print("이적시장 OPEN!\n")
    else:
        transfer_window_open = False
        print("이적시장 CLOSED\n")



def trade_player():
    if transfer_window_open:
        print("이적시장 열렸을 때는 트레이드 불가\n")
        return


    p1 = input("첫 번째 선수: ").strip()
    p2 = input("두 번째 선수: ").strip()


    idx1 = idx2 = -1
    for i, p in enumerate(players):
        if p.name == p1:
            idx1 = i
        if p.name == p2:
            idx2 = i


    if idx1 == -1 or idx2 == -1:
        print("선수 없음\n")
        return


    if abs(players[idx1].value - players[idx2].value) <= 3:
        players[idx1].team, players[idx2].team = players[idx2].team, players[idx1].team
        print("트레이드 완료!\n")
    else:
        print("가치차로 트레이드 실패\n")



def check_game_end():
    return all(p.team == "MyTeam" for p in players)



def main():
    print("=== K리그 AI 이적시장 시뮬레이터 ===")
    while True:
        print("\n1. 선수 목록")
        print("2. 선수 영입")
        print("3. 시간 진행 (2개월 + AI 업데이트)")
        print("4. 트레이드")
        print("5. 종료")
        choice = input(">> 선택: ")


        if choice == "1":
            show_all_players()
        elif choice == "2":
            transfer_player()
        elif choice == "3":
            advance_time()
        elif choice == "4":
            trade_player()
        elif choice == "5":
            print("종료합니다.")
            break
        else:
            print("잘못된 선택\n")


        if check_game_end():
            print("\n🎉 모든 선수를 영입했습니다! 게임 종료!")
            break


if __name__ == "__main__":
    main()



