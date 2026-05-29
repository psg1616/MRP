"""
===========================================
자재 소요 계획(MRP) 자동 계산기 (계산 근거 포함)
===========================================
"""

import pandas as pd
import math
from datetime import datetime, timedelta

# ============================================
# 1. 품목 기본 정보
# ============================================
items = [
    {
        "품목코드": "A-001",
        "품목명": "RF 커넥터",
        "생산필요수량": 1000,
        "현재고": 300,
        "안전재고": 200,
        "최소주문수량(MOQ)": 500,
        "리드타임(일)": 14,
        "불량률(%)": 3.0,
        "단가(원)": 1500,
        "업체명": "업체A",
    },
    {
        "품목코드": "B-002",
        "품목명": "PCB 기판",
        "생산필요수량": 500,
        "현재고": 450,
        "안전재고": 100,
        "최소주문수량(MOQ)": 200,
        "리드타임(일)": 21,
        "불량률(%)": 1.5,
        "단가(원)": 8000,
        "업체명": "업체B",
    },
    {
        "품목코드": "D-004",
        "품목명": "하우징 케이스",
        "생산필요수량": 800,
        "현재고": 900,
        "안전재고": 100,
        "최소주문수량(MOQ)": 300,
        "리드타임(일)": 10,
        "불량률(%)": 2.0,
        "단가(원)": 3000,
        "업체명": "업체D",
    },
]

# ============================================
# 2. MRP 계산 함수
# ============================================
def calculate_mrp(item, production_date):
    """품목 하나에 대한 MRP 계산 및 근거 생성"""

    # 1단계: 순소요량 계산
    net_requirement = item["생산필요수량"] + item["안전재고"] - item["현재고"]

    # 순소요량이 0 이하면 발주 불필요
    if net_requirement <= 0:
        basis_str = f"순소요량({net_requirement}개) ≤ 0 이므로 발주 불필요 (여유재고: {abs(net_requirement)}개)"
        return {
            "품목코드": item["품목코드"],
            "품목명": item["품목명"],
            "순소요량": 0,
            "발주수량": 0,
            "발주금액(원)": 0,
            "발주필요여부": "❌ 불필요",
            "발주기한": "-",
            "계산근거": basis_str
        }

    # 2단계: 불량률 보정
    defect_rate = item["불량률(%)"] / 100
    adjusted_qty = math.ceil(net_requirement / (1 - defect_rate))

    # 3단계: MOQ 적용
    moq = item["최소주문수량(MOQ)"]
    order_qty = math.ceil(adjusted_qty / moq) * moq

    # 4단계: 날짜 및 금액 계산
    order_deadline = production_date - timedelta(days=item["리드타임(일)"])
    order_amount = order_qty * item["단가(원)"]

    # 5단계: 계산 근거 문자열 조립
    basis_str = (
        f"① 순소요량: {item['생산필요수량']}(필요) + {item['안전재고']}(안전) - {item['현재고']}(재고) = {net_requirement}개\n"
        f"② 불량보정: {net_requirement} / (1 - {defect_rate}) 올림 = {adjusted_qty}개\n"
        f"③ 발주수량: {adjusted_qty}개를 MOQ({moq}개) 단위로 올림 = {order_qty}개"
    )

    return {
        "품목코드": item["품목코드"],
        "품목명": item["품목명"],
        "순소요량": net_requirement,
        "발주수량": order_qty,
        "발주금액(원)": f"{order_amount:,}",
        "발주필요여부": "✅ 필요",
        "발주기한": order_deadline.strftime("%Y-%m-%d"),
        "계산근거": basis_str
    }

# ============================================
# 3. 실행부
# ============================================
if __name__ == "__main__":
    production_date = datetime.now().date() + timedelta(days=30)

    print("=" * 60)
    print("  자재 소요 계획(MRP) 발주량 계산 근거 상세")
    print("=" * 60)

    results = []
    
    for item in items:
        result = calculate_mrp(item, production_date)
        results.append(result)

        print(f"\n📦 [{result['품목코드']}] {result['품목명']} - {result['발주필요여부']}")
        
        if result["발주필요여부"] == "✅ 필요":
            print(f"   [최종 발주량] {result['발주수량']}개 ({result['발주금액(원)']}원)")
            print(f"   [계산 근거]")
            # 계산 근거 문자열을 줄바꿈하여 예쁘게 출력
            for line in result['계산근거'].split('\n'):
                print(f"     {line}")
        else:
            print(f"   [계산 근거] {result['계산근거']}")

    # 엑셀 저장 (선택)
    try:
        df = pd.DataFrame(results)
        df.to_excel("MRP_계산근거결과.xlsx", index=False)
    except:
        pass
