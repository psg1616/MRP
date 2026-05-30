"""
===========================================
자재 소요 계획(MRP) 자동 계산기 (7일 버퍼 적용)
===========================================
"""

import pandas as pd
import math
from datetime import datetime, timedelta

# ============================================
# 1. 품목 기본 정보
# ============================================
items = [
    {"품목코드": "A-001", "품목명": "RF 커넥터", "생산필요수량": 1000, "현재고": 300, "안전재고": 200, "최소주문수량(MOQ)": 500, "리드타임(일)": 14, "불량률(%)": 3.0, "단가(원)": 1500, "업체명": "업체A"},
    {"품목코드": "B-002", "품목명": "PCB 기판", "생산필요수량": 500, "현재고": 450, "안전재고": 100, "최소주문수량(MOQ)": 200, "리드타임(일)": 21, "불량률(%)": 1.5, "단가(원)": 8000, "업체명": "업체B"},
    {"품목코드": "C-003", "품목명": "안테나 부품", "생산필요수량": 2000, "현재고": 1800, "안전재고": 300, "최소주문수량(MOQ)": 1000, "리드타임(일)": 7, "불량률(%)": 5.0, "단가(원)": 500, "업체명": "업체C"},
    {"품목코드": "D-004", "품목명": "하우징 케이스", "생산필요수량": 800, "현재고": 900, "안전재고": 100, "최소주문수량(MOQ)": 300, "리드타임(일)": 10, "불량률(%)": 2.0, "단가(원)": 3000, "업체명": "업체D"},
]

# ============================================
# 2. MRP 계산 함수
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

    # ----------------------------------------------------
    # ⭐ 여기에 작성하신 7일 버퍼 로직이 들어가야 합니다!
    # ----------------------------------------------------
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
# 3. 실행부
# ============================================
if __name__ == "__main__":
    
    # 지워졌던 생산예정일 코드 복구
    production_date = datetime.now().date() + timedelta(days=30)

    print("=" * 60)
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
