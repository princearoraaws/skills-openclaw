---
name: meituan
description: Help users make better Meituan ordering decisions from public merchant and delivery information. Use when the user wants to compare Meituan restaurants, judge whether a delivery offer is worth it, understand delivery fee, minimum order, estimated time, discount conditions, or choose between stores for takeout or local services. Especially relevant for questions like "这家值不值得点", "帮我比较这几家外卖", "满减划算吗", "配送费高不高", or "美团怎么点更划算".
---

# Meituan

Help users make better Meituan ordering decisions from public merchant and promotion information.

This is a low-sensitivity public skill. It focuses on public-page decision support and does not perform login, coupon claiming, order retrieval, cookie handling, account access, or local database persistence.

Use this skill when the user wants to:
- compare Meituan restaurants or stores
- understand whether a delivery offer is worth it
- judge delivery fee, minimum order, delivery time, and promotion conditions
- choose between stores for one-person, two-person, or group ordering

For public live-page inspection, pair it with browser-based workflows. For account pages, orders, red packets, addresses, or login-state actions, do not treat this skill as the tool for that work.

Read these references as needed:
- `references/comparison-guide.md` for merchant comparison logic
- `references/promotion-judgment.md` for discount and fee interpretation
- `references/risk-signals.md` for common takeout decision risks
- `references/output-patterns.md` for final answer structure

## Workflow

1. Identify the ordering need.
   - Accept a store, dish type, ordering scenario, or comparison request.
   - If the request is too broad, ask one short clarifying question.

2. Focus on decision-relevant public signals.
   Compare factors such as:
   - delivery fee
   - minimum order
   - estimated delivery time
   - platform discount and store discount conditions
   - rating and sales context
   - dish pricing and order threshold fit

3. Explain trade-offs.
   - A lower displayed price may still be worse if delivery fee is high.
   - A stronger discount may still be worse if the threshold is unrealistic.
   - A higher-rated store may still be worse if delivery time or basket fit is poor.

4. Give practical ordering advice.
   - Say which store looks better for the user’s scenario.
   - Mention what the user should verify before placing the order.

## Output

Use this structure unless the user asks for something shorter:

### Best Option
State the strongest current choice for the user’s scenario.

### Why
List the main reasons.

### Comparison Factors
Summarize the most important fields, such as delivery fee, minimum order, time, discount, and fit.

### Risks or Caveats
List meaningful concerns, such as weak discount conditions, high delivery fee, long wait time, or low-value bundle traps.

### Final Advice
Give a direct ordering suggestion in plain language.

## Quality bar

Do:
- focus on public merchant and promotion signals
- explain trade-offs clearly
- optimize for the user’s actual ordering scenario
- warn when a discount looks attractive but is not actually cost-effective

Do not:
- pretend to log in or inspect account-only pages
- claim to retrieve orders, coupons, or red packets
- store cookies or account data
- present public-page heuristics as guaranteed outcomes
