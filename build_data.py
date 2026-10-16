"""팬딩 멤버십 가입자/이탈자 엑셀 두 개로 사이트용 data.json을 만듭니다.

사용법: python scripts/build_data.py 멤버십가입자목록_*.xlsx 멤버십이탈자목록_*.xlsx 2026-10-16
data.json에는 닉네임·연락처 같은 개인 정보 없이 집계 숫자만 들어갑니다.
"""
import sys, json, datetime as dt
import pandas as pd

LAUNCH = dt.date(2025, 8, 1)
GROUPS = ['3Package', '프리미엄 Package', '3+프리미엄', '기타']
REASONS = ['활동 부족', '리워드 불만족', '목표 리워드 달성', '가격 부담', '팬딩 서비스 불만족']


def group(plan):
    p = str(plan)
    if '3Package+프리미엄' in p.replace(' ', ''):
        return '3+프리미엄'
    if '프리미엄 Package' in p:
        return '프리미엄 Package'
    if '3Package' in p:
        return '3Package'
    return '기타'


def main(join_xlsx, churn_xlsx, as_of):
    j = pd.read_excel(join_xlsx)
    c = pd.read_excel(churn_xlsx)
    active = [dict(month=str(r['최초 가입 일자'])[:7], group=group(r['가입 중인 플랜명'])) for _, r in j.iterrows()]
    churned = []
    for _, r in c.iterrows():
        d = dt.date.fromisoformat(str(r['이탈 일자'])[:10])
        rd = int(r['마지막 이용 회차'])
        est = max(d - dt.timedelta(days=rd * 30 - 1), LAUNCH)  # 이탈자는 가입일이 없어 추정
        churned.append(dict(churn=d.isoformat()[:7], est=est.isoformat()[:7], group=group(r['마지막 이용 플랜명']),
                            reasons=[REASONS[k] for k in range(5) if r[c.columns[5 + k]] == 'O']))
    allm = sorted([a['month'] for a in active] + [x['churn'] for x in churned] + [x['est'] for x in churned])
    months, (y, m) = [], map(int, allm[0].split('-'))
    while True:
        k = f'{y}-{m:02d}'
        months.append(k)
        if k >= allm[-1]:
            break
        m += 1
        if m > 12:
            y, m = y + 1, 1
    monthly, totals, reasons = [], [], []
    for g in ['all'] + GROUPS:
        A = [a for a in active if g == 'all' or a['group'] == g]
        C = [x for x in churned if g == 'all' or x['group'] == g]
        prev = None
        for mo in months:
            joins = sum(a['month'] == mo for a in A) + sum(x['est'] == mo for x in C)
            churns = sum(x['churn'] == mo for x in C)
            act = sum(a['month'] <= mo for a in A) + sum(x['est'] <= mo < x['churn'] for x in C)
            row = dict(group=g, month=mo, joins=joins, churns=churns, net=joins - churns, active_end=act,
                       joins_delta=None if prev is None else joins - prev['joins'],
                       churns_delta=None if prev is None else churns - prev['churns'])
            monthly.append(row)
            prev = row
        totals.append(dict(group=g, total_joins=len(A) + len(C), total_churns=len(C), current_active=len(A)))
        for rs in REASONS:
            reasons.append(dict(group=g, reason=rs, n=sum(rs in x['reasons'] for x in C)))
    out = dict(as_of=as_of, groups=GROUPS, monthly=monthly, totals=totals, reasons=reasons)
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print('data.json 저장:', len(months), '개월, 현재 활성', len(active), '명')


if __name__ == '__main__':
    main(*sys.argv[1:4])
