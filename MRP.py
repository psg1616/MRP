"""
===========================================
자재 소요 계획(MRP) 최종판 (계산 근거 포함)
===========================================
- 엑셀 행 복사/붙여넣기 입력 지원
- 품목별 개별 날짜 및 버퍼 적용
- 발주수량 및 날짜 역산 상세 계산 근거 제공
"""

import pandas as pd
import math
from datetime import datetime, timedelta

# ============================================
# 1. MRP 계산 함수 (계산 근거 로직 추가)
# ============================================
def calculate_mrp(item):
    # 1단계: 순소요량 계산
    net_requirement = item["생산필요수량"] + item["안전재고"] - item["현재고"]

    # 발주 불필요 케이스
    if net_requirement <= 0:
        basis_str = f"순소요량({net_requirement}개) ≤ 0 이므로 발주 불필요 (여유재고: {abs(net_requirement)}개)"
        return {
            "품목코드": item["품목코드"], "품목명": item["품목명"], "생산예정일": item["생산예정일"].strftime("%Y-%m-%d"),
            "업체명": item["업체명"], "생산필요수량": item["생산필요수량"], "현재고": item["현재고"],
            "안전재고": item["안전재고"], "최소주문수량": item["최소주문수량(MOQ)"], "순소요량": 0, "불량보정수량": 0, "MOQ적용_발주수량": 0,
            "발주금액(원)": 0, "발주필요여부": "❌ 불필요", "발주기한": "-", "여유재고": abs(net_requirement),
            "계산근거": basis_str
        }

    # 2단계: 불량률 보정
    defect_rate = item["불량률(%)"] / 100
    adjusted_qty = math.ceil(net_requirement / (1 - defect_rate))
    
    # 3단계: MOQ 적용
    moq = item["최소주문수량(MOQ)"]
    order_qty = math.ceil(adjusted_qty / moq) * moq

    # 4단계: 버퍼 및 리드타임 적용 기한 역산
    buffer_days = item["입고버퍼(일)"]
    production_date = item["생산예정일"]
    order_deadline = production_date - timedelta(days=(item["리드타임(일)"] + buffer_days))
    
    today = datetime.now().date()
    days_left = (order_deadline - today).days

    # 긴급도 판단
    if days_left < 0: urgency = "🚨 기한 초과!"
    elif days_left <= 3: urgency = "⚠️ 긴급"
    elif days_left <= 7: urgency = "📋 주의"
    else: urgency = "✅ 여유"

    order_amount = order_qty * item["단가(원)"]

    # 5단계: 상세 계산 근거 문자열 조립
    basis_str = (
        f"① 순소요량: {item['생산필요수량']}(필요) + {item['안전재고']}(안전) - {item['현재고']}(재고) = {net_requirement}개\n"
        f"② 불량보정: {net_requirement} / (1 - {defect_rate}) 올림 = {adjusted_qty}개\n"
        f"③ 발주수량: {adjusted_qty}개를 MOQ({moq}개) 단위로 올림 = {order_qty}개\n"
        f"④ 발주기한: {production_date.strftime('%Y-%m-%d')} - (리드타임 {item['리드타임(일)']}일 + 버퍼 {buffer_days}일) = {order_deadline.strftime('%Y-%m-%d')}"
    )

    return {
        "품목코드": item["품목코드"], "품목명": item["품목명"], "생산예정일": production_date.strftime("%Y-%m-%d"),
        "업체명": item["업체명"], "생산필요수량": item["생산필요수량"], "현재고": item["현재고"],
        "안전재고": item["안전재고"], "최소주문수량": item["최소주문수량(MOQ)"], "순소요량": net_requirement, "불량보정수량": adjusted_qty,
        "MOQ적용_발주수량": order_qty, "발주금액(원)": f"{order_amount:,}", "발주필요여부": "✅ 필요",
        "발주기한": order_deadline.strftime("%Y-%m-%d"), "긴급도": urgency, "남은일수": f"{days_left}일",
        "계산근거": basis_str
    }

# ============================================
# 2. 메인 실행부
# ============================================
if __name__ == "__main__":
    print("=" * 70)
    print(" 📊 자재 소요 계획(MRP) '상세 근거 포함' 계산기")
    print("=" * 70)

    items = []
    
    while True:
        print("\n📦 [데이터 붙여넣기]")
        print("엑셀에서 아래 12개 항목을 순서대로 드래그 복사(Ctrl+C)하여 붙여넣으세요(Ctrl+V).")
        print("(순서: 예정일 | 코드 | 품목명 | 필요수량 | 현재고 | 안전재고 | MOQ | 리드타임 | 버퍼 | 불량률 | 단가 | 업체명)")
        
        raw_input = input("\n▶ 입력 (쉼표 또는 엑셀 복붙): ").strip()
        
        if not raw_input:
            continue
            
        if '\t' in raw_input:
            data_parts = raw_input.split('\t')
        else:
            data_parts = [x.strip() for x in raw_input.split(',')]
            
        if len(data_parts) != 12:
            print(f"\n  ❌ 오류: 12개의 항목이 필요하지만, {len(data_parts)}개가 입력되었습니다.")
            print("  열 순서와 개수를 다시 확인해 주세요.")
            continue
            
        try:
            prod_date = datetime.strptime(data_parts[0].strip(), "%Y-%m-%d").date()
            
            item = {
                "생산예정일": prod_date,
                "품목코드": data_parts[1].strip(),
                "품목명": data_parts[2].strip(),
                "생산필요수량": int(data_parts[3]),
                "현재고": int(data_parts[4]),
                "안전재고": int(data_parts[5]),
                "최소주문수량(MOQ)": int(data_parts[6]),
                "리드타임(일)": int(data_parts[7]),
                "입고버퍼(일)": int(data_parts[8]),
                "불량률(%)": float(data_parts[9]),
                "단가(원)": int(data_parts[10]),
                "업체명": data_parts[11].strip()
            }
            items.append(item)
            print(f"  ✅ '{item['품목명']}' 항목이 성공적으로 등록되었습니다.")
            
        except ValueError as e:
            print("\n  ❌ 오류: 날짜 형식(YYYY-MM-DD)이 틀렸거나, 숫자가 들어가야 할 곳에 문자가 있습니다.")
            print("  데이터를 다시 확인하고 붙여넣어 주세요.")
            continue 

        more = input("\n▶ 다른 품목을 더 붙여넣으시겠습니까? (y / n): ").strip().lower()
        if more != 'y':
            break

    # --- 결과 출력 및 저장 ---
    if items:
        print("\n\n" + "=" * 70)
        print(f"  자재 소요 계획(MRP) 계산 결과 상세")
        print("=" * 70)

        results = []
        total_order_amount = 0

        for item in items:
            result = calculate_mrp(item)
            results.append(result)

            print(f"\n📦 [{result['품목코드']}] {result['품목명']}")
            print(f"   업체: {result['업체명']} | 생산예정일: {result['생산예정일']}")
            print(f"   생산필요: {result['생산필요수량']}개 | 현재고: {result['현재고']}개 | 안전재고: {result['안전재고']}개 | 최소주문수량: {result['최소주문수량']}개")
            print(f"   순소요량: {result['순소요량']}개")
            print(f"   발주필요: {result['발주필요여부']}")

            if result["발주필요여부"] == "✅ 필요":
                print(f"   불량보정: {result['불량보정수량']}개 → MOQ적용: {result['MOQ적용_발주수량']}개")
                print(f"   발주금액: {result['발주금액(원)']}원")
                print(f"   발주기한: {result['발주기한']} ({result['긴급도']} {result['남은일수']})")
                
                # 금액 합산
                amount = int(result["발주금액(원)"].replace(",", ""))
                total_order_amount += amount
                
                # 계산 근거 출력
                print("   [계산 근거]")
                for line in result['계산근거'].split('\n'):
                    print(f"     {line}")
            else:
                print(f"   여유재고: {result['여유재고']}개")
                print(f"   [계산 근거] {result['계산근거']}")

        print("\n" + "=" * 70)
        print(f"  💰 총 발주 예상 금액: {total_order_amount:,}원")
        print("=" * 70)

        try:
            df = pd.DataFrame(results)
            filename = f"MRP_결과_근거포함_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            df.to_excel(filename, index=False)
            print(f"\n📊 엑셀 파일 저장 완료: {filename}\n")
        except Exception as e:
            pass
    else:
        print("\n입력된 데이터가 없어 프로그램을 종료합니다.")
