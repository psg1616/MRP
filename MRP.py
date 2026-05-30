"""
===========================================
자재 소요 계획(MRP) 대화형 계산기 (최종 실무판)
===========================================
- 품목별로 다른 생산 예정일 및 입고 버퍼 개별 적용
"""

import pandas as pd
import math
from datetime import datetime, timedelta

# ============================================
# 1. MRP 계산 함수
# ============================================
def calculate_mrp(item):
    """품목 하나에 대한 MRP 계산 (개별 일정 반영)"""
    
    net_requirement = item["생산필요수량"] + item["안전재고"] - item["현재고"]

    if net_requirement <= 0:
        return {
            "품목코드": item["품목코드"],
            "품목명": item["품목명"],
            "생산예정일": item["생산예정일"].strftime("%Y-%m-%d"),
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

    # ⭐ 품목별로 입력받은 개별 버퍼와 생산일 적용
    buffer_days = item["입고버퍼(일)"]
    production_date = item["생산예정일"]
    
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
        "생산예정일": production_date.strftime("%Y-%m-%d"),
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
    print(" 📊 자재 소요 계획(MRP) 개별 맞춤형 계산기")
    print("=" * 60)

    items = []
    
    # --- 품목 데이터 개별 입력받기 ---
    while True:
        print("\n" + "-" * 50)
        print(" 📦 [새로운 품목 정보 입력]")
        print("-" * 50)
        
        try:
            # 날짜 입력을 먼저 별도로 처리 (형식 오류 방지)
            date_str = input(" 1. 생산 예정일 (예: 2026-06-30): ").strip()
            prod_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            item = {
                "생산예정일": prod_date,
                "품목코드": input(" 2. 품목코드 (예: A-001): ").strip(),
                "품목명": input(" 3. 품목명 (예: RF 커넥터): ").strip(),
                "생산필요수량": int(input(" 4. 생산필요수량 (개): ")),
                "현재고": int(input(" 5. 현재고 (개): ")),
                "안전재고": int(input(" 6. 안전재고 (개): ")),
                "최소주문수량(MOQ)": int(input(" 7. 최소주문수량(MOQ): ")),
                "리드타임(일)": int(input(" 8. 납품 리드타임(일): ")),
                "입고버퍼(일)": int(input(" 9. 입고 후 대기 버퍼(일): ")),
                "불량률(%)": float(input(" 10. 불량률(%) (예: 3.0): ")),
                "단가(원)": int(input(" 11. 단가(원): ")),
                "업체명": input(" 12. 업체명: ").strip()
            }
            items.append(item)
            
        except ValueError:
            print("\n  ❌ 오류: 날짜 형식(YYYY-MM-DD)이 틀렸거나 숫자가 아닌 값을 입력했습니다.")
            print("  이 품목의 입력을 처음부터 다시 진행합니다.")
            continue 

        # 추가 입력 여부 확인
        more = input("\n▶ 다른 품목을 추가로 입력하시겠습니까? (y / n): ").strip().lower()
        if more != 'y':
            break

    # --- 결과 계산 및 출력 ---
    print("\n\n" + "=" * 60)
    print(f"  자재 소요 계획(MRP) 개별 계산 결과")
    print(f"  계산일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    results = []
    total_order_amount = 0

    for item in items:
        result = calculate_mrp(item) # 품목 정보 안에 날짜가 있으므로 인자를 하나만 넘김
        results.append(result)

        print(f"\n📦 [{result['품목코드']}] {result['품목명']}")
        print(f"   업체: {result['업체명']} | 생산예정일: {result['생산예정일']}")
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

    # --- 엑셀 자동 저장 ---
    try:
        df = pd.DataFrame(results)
        filename = f"MRP_결과_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        df.to_excel(filename, index=False)
        print(f"\n📊 엑셀 파일 저장 완료: {filename}\n")
    except Exception as e:
        pass
