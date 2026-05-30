"""
===========================================
자재 소요 계획(MRP) 대화형 계산기
===========================================
- 코드를 수정할 필요 없이 실행 후 값만 입력
- 7일 입고 버퍼 로직 반영
"""

import pandas as pd
import math
from datetime import datetime, timedelta
import sys

# ============================================
# 1. MRP 계산 함수 (핵심 로직 유지)
# ============================================
def calculate_mrp(item, production_date):
    """품목 하나에 대한 MRP 계산"""
    net_requirement = item["생산필요수량"] + item["안전재고"] - item["현재고"]

    if net_requirement <= 0:
        return {
            "품목코드": item["품목코드"],
            "품목명": item["품목명"],
            "업체명": item["업체명"],
            "생산필요수량": item["생산필요수량"],
            "현재고": item["현재고"],
            "안전재고": item["안전재고"],
            "순소요량": 0,
            "불량보정수량": 0,
            "MOQ적용_발주수량": 0,
            "발주금액(원)": 0,
            "발주필요여부": "❌ 불필요",
            "발주기한": "-",
            "여유재고": abs(net_requirement),
        }

    defect_rate = item["불량률(%)"] / 100
    adjusted_qty = math.ceil(net_requirement / (1 - defect_rate))

    moq = item["최소주문수량(MOQ)"]
    order_qty = math.ceil(adjusted_qty / moq) * moq

    # 7일 입고 버퍼 적용
    buffer_days = 7 
    order_deadline = production_date - timedelta(days=(item["리드타임(일)"] + buffer_days))
    
    today = datetime.now().date()
    days_left = (order_deadline - today).days

    # 긴급도 판단
    if days_left < 0:
        urgency = "🚨 기한 초과!"
    elif days_left <= 3:
        urgency = "⚠️ 긴급"
    elif days_left <= 7:
        urgency = "📋 주의"
    else:
        urgency = "✅ 여유"

    order_amount = order_qty * item["단가(원)"]

    return {
        "품목코드": item["품목코드"],
        "품목명": item["품목명"],
        "업체명": item["업체명"],
        "생산필요수량": item["생산필요수량"],
        "현재고": item["현재고"],
        "안전재고": item["안전재고"],
        "순소요량": net_requirement,
        "불량보정수량": adjusted_qty,
        "MOQ적용_발주수량": order_qty,
        "발주금액(원)": f"{order_amount:,}",
        "발주필요여부": "✅ 필요",
        "발주기한": order_deadline.strftime("%Y-%m-%d"),
        "긴급도": urgency,
        "남은일수": f"{days_left}일",
    }

# ============================================
# 2. 메인 실행부 (사용자 입력 로직)
# ============================================
if __name__ == "__main__":
    print("=" * 60)
    print(" 📊 자재 소요 계획(MRP) 대화형 계산기")
    print("=" * 60)

    # --- [1] 생산 예정일 입력받기 ---
    while True:
        try:
            date_str = input("\n▶ 생산 예정일을 입력하세요 (예: 2026-06-30): ").strip()
            production_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            break
        except ValueError:
            print("  ❌ 오류: 날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 다시 입력해주세요.")

    items = []
    
    # --- [2] 품목 데이터 반복 입력받기 ---
    while True:
        print("\n" + "-" * 40)
        print(" 📦 [새로운 품목 정보 입력]")
        print("-" * 40)
        
        try:
            item = {
                "품목코드": input(" 1. 품목코드 (예: A-001): ").strip(),
                "품목명": input(" 2. 품목명 (예: RF 커넥터): ").strip(),
                "생산필요수량": int(input(" 3. 생산필요수량 (개): ")),
                "현재고": int(input(" 4. 현재고 (개): ")),
                "안전재고": int(input(" 5. 안전재고 (개): ")),
                "최소주문수량(MOQ)": int(input(" 6. 최소주문수량(MOQ): ")),
                "리드타임(일)": int(input(" 7. 리드타임(일): ")),
                "불량률(%)": float(input(" 8. 불량률(%) (예: 3.0): ")),
                "단가(원)": int(input(" 9. 단가(원): ")),
                "업체명": input(" 10. 업체명: ").strip()
            }
            items.append(item)
            
        except ValueError:
            print("\n  ❌ 오류: 수량, 리드타임, 단가 등에는 숫자만 입력해야 합니다. 처음부터 다시 입력해주세요.")
            continue # 에러 나면 현재 품목 입력을 취소하고 다시 시작

        # 추가 입력 여부 확인
        more = input("\n▶ 다른 품목을 추가로 입력하시겠습니까? (y / n): ").strip().lower()
        if more != 'y':
            break

    # --- [3] 결과 계산 및 출력 ---
    print("\n\n" + "=" * 60)
    print(f"  자재 소요 계획(MRP) 계산 결과 (입고 버퍼 7일 반영)")
    print(f"  생산예정일: {production_date.strftime('%Y-%m-%d')}")
    print(f"  계산일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    results = []
    total_order_amount = 0

    for item in items:
        result = calculate_mrp(item, production_date)
        results.append(result)

        print(f"\n📦 [{result['품목코드']}] {result['품목명']}")
        print(f"   업체: {result['업체명']}")
        print(f"   생산필요: {result['생산필요수량']}개 | 현재고: {result['현재고']}개 | 안전재고: {result['안전재고']}개")
        print(f"   순소요량: {result['순소요량']}개")
        print(f"   발주필요: {result['발주필요여부']}")

        if result["발주필요여부"] == "✅ 필요":
            print(f"   불량보정: {result['불량보정수량']}개 → MOQ적용: {result['MOQ적용_발주수량']}개")
            print(f"   발주금액: {result['발주금액(원)']}원")
            print(f"   발주기한: {result['발주기한']} ({result['긴급도']} {result['남은일수']})")
            amount = int(result["발주금액(원)"].replace(",", ""))
            total_order_amount += amount
        else:
            print(f"   여유재고: {result['여유재고']}개")

    print("\n" + "=" * 60)
    print(f"  💰 총 발주 예상 금액: {total_order_amount:,}원")
    print("=" * 60)

    # --- [4] 엑셀 자동 저장 ---
    try:
        df = pd.DataFrame(results)
        filename = f"MRP_결과_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        df.to_excel(filename, index=False)
        print(f"\n📊 엑셀 파일 저장 완료: {filename}\n")
    except Exception as e:
        pass
